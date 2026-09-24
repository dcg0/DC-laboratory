from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CSP = (
    "default-src 'self'; "
    "base-uri 'none'; "
    "object-src 'none'; "
    "frame-ancestors 'none'; "
    "form-action 'self'; "
    "script-src 'self' 'unsafe-inline'; "
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
    "font-src 'self' https://fonts.gstatic.com; "
    "img-src 'self' data: https:; "
    "media-src 'self'; "
    "connect-src 'self'; "
    "upgrade-insecure-requests"
)

SECURITY_META = (
    f'<meta http-equiv="Content-Security-Policy" content="{CSP}">\n'
    '  <meta name="referrer" content="strict-origin-when-cross-origin">\n'
    '  <meta http-equiv="X-Content-Type-Options" content="nosniff">\n'
    '  <meta http-equiv="Permissions-Policy" content="camera=(), microphone=(), geolocation=(), payment=()">'
)

for path in sorted(ROOT.glob("*.html")):
    text = path.read_text(encoding="utf-8")
    if 'http-equiv="Content-Security-Policy"' not in text:
        marker = '<meta name="viewport"'
        start = text.find(marker)
        if start == -1:
            raise SystemExit(f"No viewport meta found in {path}")
        end = text.find('>', start)
        if end == -1:
            raise SystemExit(f"Malformed viewport meta in {path}")
        text = text[: end + 1] + "\n  " + SECURITY_META + text[end + 1 :]
    text = text.replace(
        "if(alert)alert.innerHTML=rule?'<strong>Alerta preventiva</strong> '+rule[1]:'<strong>Tip de Lucy</strong> Usa filtros, responsables y respaldos para mantener una operación estable.';",
        "if(alert)alert.textContent=rule?'Alerta preventiva '+rule[1]:'Tip de Lucy Usa filtros, responsables y respaldos para mantener una operación estable.';",
    )
    path.write_text(text, encoding="utf-8")

(ROOT / "robots.txt").write_text(
    "User-agent: *\nAllow: /\nDisallow: /admin.html\n",
    encoding="utf-8",
)

(ROOT / ".well-known").mkdir(exist_ok=True)
(ROOT / ".well-known" / "security.txt").write_text(
    "Contact: https://github.com/dcg0/DC-laboratory/security/advisories/new\n"
    "Preferred-Languages: es, en\n"
    "Canonical: https://dcg0.github.io/DC-laboratory/.well-known/security.txt\n",
    encoding="utf-8",
)

(ROOT / "_headers").write_text(
    "/*\n"
    "  Content-Security-Policy: " + CSP + "\n"
    "  X-Content-Type-Options: nosniff\n"
    "  X-Frame-Options: DENY\n"
    "  Referrer-Policy: strict-origin-when-cross-origin\n"
    "  Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=()\n"
    "  Strict-Transport-Security: max-age=31536000; includeSubDomains; preload\n"
    "  Cross-Origin-Opener-Policy: same-origin\n"
    "  Cross-Origin-Resource-Policy: same-origin\n"
    "\n"
    "/downloads/*\n"
    "  X-Content-Type-Options: nosniff\n"
    "  Content-Disposition: attachment\n",
    encoding="utf-8",
)

print(f"Hardened {len(list(ROOT.glob('*.html')))} HTML pages")
print("Updated robots.txt, .well-known/security.txt and _headers")
