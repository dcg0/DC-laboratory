#!/usr/bin/env python3
"""Static integrity checks for the DC Laboratory GitHub Pages site."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
HOST = "dcg0.github.io"
PROJECT_PREFIX = "/DC-laboratory"
SITEMAP_URL = "https://dcg0.github.io/DC-laboratory/sitemap.xml"
IGNORED_DIRS = {".git", "node_modules", ".venv"}

failures: list[str] = []


class PageParser(HTMLParser):
    def __init__(self, page: Path) -> None:
        super().__init__(convert_charrefs=True)
        self.page = page
        self.ids: set[str] = set()
        self.duplicate_ids: set[str] = set()
        self.references: list[tuple[str, str]] = []
        self.description_count = 0
        self.canonical_count = 0
        self.has_csp = False
        self.has_referrer = False
        self.has_script_src_self = False
        self.has_noindex = False
        self.has_html_lang = False

    def handle_starttag(self, tag: str, raw_attrs: list[tuple[str, str | None]]) -> None:
        attrs = dict(raw_attrs)
        if tag == "html":
            self.has_html_lang = bool(attrs.get("lang"))

        identifier = attrs.get("id")
        if identifier:
            if identifier in self.ids:
                self.duplicate_ids.add(identifier)
            self.ids.add(identifier)

        if tag == "img" and "alt" not in attrs:
            failures.append(f"{self.page}: <img> sin atributo alt")

        for key in attrs:
            if key.lower().startswith("on"):
                failures.append(f"{self.page}: manejador inline {key}= no permitido")
        if tag == "a" and attrs.get("target", "").lower() == "_blank":
            rel = {item.lower() for item in (attrs.get("rel") or "").split()}
            if "noopener" not in rel:
                failures.append(f"{self.page}: target=_blank sin rel=noopener")

        if tag == "meta":
            http_equiv = (attrs.get("http-equiv") or "").lower()
            name = (attrs.get("name") or "").lower()
            if http_equiv == "content-security-policy":
                self.has_csp = True
                policy = attrs.get("content") or ""
                directive = next(
                    (part.strip() for part in policy.split(";") if part.strip().lower().startswith("script-src ")),
                    "",
                )
                self.has_script_src_self = "'self'" in directive.lower().split()
                if "'unsafe-inline'" in directive.lower().split():
                    failures.append(f"{self.page}: script-src permite unsafe-inline")
                if "frame-ancestors" in policy.lower():
                    failures.append(f"{self.page}: frame-ancestors no es efectivo en una meta CSP")
            elif http_equiv in {"x-content-type-options", "permissions-policy", "x-frame-options"}:
                failures.append(f"{self.page}: meta http-equiv={http_equiv} no configura una cabecera HTTP")
            if name == "referrer":
                self.has_referrer = True
            elif name == "description":
                self.description_count += 1
            elif name == "robots" and "noindex" in (attrs.get("content") or "").lower():
                self.has_noindex = True
        elif tag == "link":
            if "canonical" in (attrs.get("rel") or "").lower().split():
                self.canonical_count += 1

        ref_attrs = {
            "a": ("href",),
            "area": ("href",),
            "img": ("src",),
            "script": ("src",),
            "link": ("href",),
            "source": ("src", "srcset"),
            "video": ("src", "poster"),
            "audio": ("src",),
            "track": ("src",),
            "iframe": ("src",),
            "object": ("data",),
        }
        for attr in ref_attrs.get(tag, ()):
            value = attrs.get(attr)
            if not value:
                continue
            if attr == "srcset":
                for candidate in value.split(","):
                    parts = candidate.strip().split()
                    if parts:
                        self.references.append((parts[0], "srcset"))
            else:
                self.references.append((value.strip(), attr))

        if tag == "script" and not attrs.get("src"):
            script_type = (attrs.get("type") or "").lower()
            if script_type not in {"application/ld+json", "application/json", "text/plain"}:
                failures.append(f"{self.page}: JavaScript inline no permitido; usar archivo local")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)


html_pages = sorted(
    path
    for path in ROOT.rglob("*.html")
    if not (set(path.parts) & IGNORED_DIRS)
)
if not html_pages:
    failures.append("No hay páginas HTML")

parsers: dict[Path, PageParser] = {}
for page in html_pages:
    parser = PageParser(page.relative_to(ROOT))
    try:
        parser.feed(page.read_text(encoding="utf-8", errors="strict"))
        parser.close()
    except (OSError, UnicodeError) as exc:
        failures.append(f"{page.relative_to(ROOT)}: no se pudo leer/parsear: {exc}")
        continue
    parsers[page.resolve()] = parser
    if parser.duplicate_ids:
        failures.append(f"{page.relative_to(ROOT)}: ids duplicados {sorted(parser.duplicate_ids)}")
    if not parser.has_html_lang:
        failures.append(f"{page.relative_to(ROOT)}: falta lang en <html>")
    if not parser.has_csp or not parser.has_script_src_self:
        failures.append(f"{page.relative_to(ROOT)}: falta CSP meta con script-src 'self'")
    if not parser.has_referrer:
        failures.append(f"{page.relative_to(ROOT)}: falta meta name=referrer")
    is_exempt = page.name in {"admin.html"} or parser.has_noindex
    if not is_exempt:
        if not page.with_suffix(".html").exists():
            failures.append(f"{page.relative_to(ROOT)}: archivo no disponible")
        if parser.description_count != 1:
            failures.append(f"{page.relative_to(ROOT)}: se requiere una única meta description")
        if parser.canonical_count != 1:
            failures.append(f"{page.relative_to(ROOT)}: se requiere un único canonical")


def resolve_reference(source: Path, raw_url: str) -> tuple[Path | None, str, bool]:
    """Return (target file, decoded fragment, whether the reference is local)."""
    value = raw_url.strip()
    parts = urlsplit(value)
    if parts.scheme.lower() == "javascript":
        failures.append(f"{source}: URL javascript: no permitida ({value[:100]})")
        return None, "", True
    if parts.scheme.lower() in {"mailto", "tel", "data", "blob", "about"}:
        return None, "", False
    if parts.scheme and parts.scheme.lower() not in {"http", "https"}:
        return None, "", False
    same_host = parts.netloc.lower() == HOST
    if value.startswith("//") and not same_host:
        return None, "", False
    if parts.netloc and not same_host:
        return None, "", False

    path_text = unquote(parts.path)
    if same_host:
        if path_text in {PROJECT_PREFIX, PROJECT_PREFIX + "/"}:
            target = ROOT
        elif path_text.startswith(PROJECT_PREFIX + "/"):
            target = ROOT / path_text[len(PROJECT_PREFIX) + 1:]
        else:
            return None, "", False
    elif path_text.startswith("/"):
        if path_text.startswith(PROJECT_PREFIX + "/"):
            target = ROOT / path_text[len(PROJECT_PREFIX) + 1:]
        else:
            failures.append(f"{source}: ruta absoluta fuera de la base de GitHub Pages ({value})")
            return None, unquote(parts.fragment), True
    elif path_text:
        target = (ROOT / source.parent / path_text).resolve()
    else:
        target = (ROOT / source).resolve()

    try:
        target.relative_to(ROOT.resolve())
    except ValueError:
        failures.append(f"{source}: ruta sale del repositorio ({value})")
        return None, unquote(parts.fragment), True
    if target.is_dir():
        target = target / "index.html"
    return target, unquote(parts.fragment), True


for abs_page, parser in parsers.items():
    source = abs_page.relative_to(ROOT.resolve())
    for raw_url, attr in parser.references:
        target, fragment, local = resolve_reference(source, raw_url)
        if not local or target is None:
            continue
        if not target.is_file():
            failures.append(f"{source}: {attr} local no encontrado: {raw_url}")
            continue
        if fragment and target.suffix.lower() == ".html":
            target_parser = parsers.get(target.resolve())
            if target_parser is None:
                target_parser = PageParser(target.relative_to(ROOT))
                try:
                    target_parser.feed(target.read_text(encoding="utf-8", errors="strict"))
                    target_parser.close()
                    parsers[target.resolve()] = target_parser
                except (OSError, UnicodeError):
                    failures.append(f"{source}: no se pudo comprobar el fragmento de {raw_url}")
                    continue
            if fragment not in target_parser.ids:
                failures.append(f"{source}: fragmento #{fragment} inexistente en {target.relative_to(ROOT)}")

# Validate the static sitemap and avoid advertising private/non-indexable routes.
sitemap_path = ROOT / "sitemap.xml"
robots_path = ROOT / "robots.txt"
if not sitemap_path.is_file():
    failures.append("Falta sitemap.xml")
else:
    try:
        root = ET.parse(sitemap_path).getroot()
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locations = [node.text or "" for node in root.findall("s:url/s:loc", ns)]
        if not locations:
            failures.append("sitemap.xml no contiene URLs")
        if SITEMAP_URL not in robots_path.read_text(encoding="utf-8") if robots_path.is_file() else True:
            failures.append("robots.txt no anuncia el sitemap.xml")
        for location in locations:
            target, _fragment, local = resolve_reference(Path("index.html"), location)
            if not local or target is None or not target.is_file():
                failures.append(f"sitemap.xml: URL sin página local válida: {location}")
            elif target.name == "admin.html":
                failures.append("sitemap.xml no debe listar admin.html")
            elif target.resolve() in parsers and parsers[target.resolve()].has_noindex:
                failures.append(f"sitemap.xml no debe listar noindex: {location}")
    except (ET.ParseError, OSError) as exc:
        failures.append(f"No se pudo validar sitemap.xml: {exc}")

if failures:
    print("\n".join(f"FAIL: {item}" for item in failures), file=sys.stderr)
    raise SystemExit(f"Fallaron {len(failures)} validaciones estáticas")

print(
    f"OK: {len(html_pages)} páginas; CSP sin unsafe-inline; enlaces, anclas, imágenes, "
    "metadatos, sitemap y relaciones noopener verificados."
)
