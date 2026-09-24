from pathlib import Path

path = Path(__file__).resolve().parents[1] / "admin.html"
text = path.read_text(encoding="utf-8")

old = '<input id="question" autocomplete="off" placeholder="Escribe tu pregunta…">'
new = '<input id="question" autocomplete="off" maxlength="240" spellcheck="false" aria-label="Pregunta para Lucy" placeholder="Escribe tu pregunta…">'
if old not in text:
    raise SystemExit("question input not found")
text = text.replace(old, new, 1)

old = '<section id="instalacion" class="help">'
new = '<div class="note" role="note"><strong>Uso público:</strong> esta página no es un panel privado y no solicita credenciales. No escribas contraseñas, tokens, datos fiscales ni información personal.</div><section id="instalacion" class="help">'
if old not in text:
    raise SystemExit("installation section not found")
text = text.replace(old, new, 1)

old = "const messages=document.getElementById('messages'),form=document.getElementById('chat-form'),input=document.getElementById('question');"
new = "const messages=document.getElementById('messages'),form=document.getElementById('chat-form'),input=document.getElementById('question');const requestWindow=[];let lastRequest=0;"
if old not in text:
    raise SystemExit("chat constants not found")
text = text.replace(old, new, 1)

old = "function ask(q){if(!q.trim())return;addMessage(q,'user');addMessage(reply(q));messages.scrollTop=messages.scrollHeight}"
new = "function ask(q){const clean=q.replace(/[\\u0000-\\u001f\\u007f]/g,' ').trim().slice(0,240);const now=Date.now();while(requestWindow.length&&now-requestWindow[0]>60000)requestWindow.shift();if(!clean||now-lastRequest<1500||requestWindow.length>=8){if(requestWindow.length>=8)addMessage('Límite temporal alcanzado. Espera un minuto antes de enviar más consultas.');return}lastRequest=now;requestWindow.push(now);addMessage(clean,'user');addMessage(reply(clean));messages.scrollTop=messages.scrollHeight}"
if old not in text:
    raise SystemExit("ask function not found")
text = text.replace(old, new, 1)

path.write_text(text, encoding="utf-8")
print("admin.html now has public-use warning, input limits and client-side abuse throttling")
