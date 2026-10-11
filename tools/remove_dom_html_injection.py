from pathlib import Path

path = Path(__file__).resolve().parents[1] / "admin.html"
text = path.read_text(encoding="utf-8")
old = "const escapeHtml=s=>s.replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));"
new = "const addMessage=(text,kind='')=>{const el=document.createElement('div');el.className=kind?'msg '+kind:'msg';el.textContent=text;messages.appendChild(el)};"
if old not in text:
    raise SystemExit("escapeHtml declaration not found")
text = text.replace(old, new, 1)
old = "messages.insertAdjacentHTML('beforeend',`<div class=\"msg user\">${escapeHtml(q)}</div><div class=\"msg\">${reply(q)}</div>`);"
new = "addMessage(q,'user');addMessage(reply(q));"
if old not in text:
    raise SystemExit("unsafe message rendering not found")
text = text.replace(old, new, 1)
path.write_text(text, encoding="utf-8")
print("admin.html now renders chat messages with DOM textContent")
