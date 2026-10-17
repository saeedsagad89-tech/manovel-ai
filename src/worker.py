import json
from urllib.parse import urlparse

from js import Object, fetch
from pyodide.ffi import to_js
from workers import WorkerEntrypoint, Response

MODEL = "gemini-3.8-flash"

SYSTEM_PROMPT = """أنت MANOVEL AI، مساعد عربي متخصص في كتابة الروايات والمانهوا والقصص الطويلة.
ساعد المستخدم في بناء الشخصيات والعوالم والحبكات والحوار والمشاهد، وفي مراجعة النصوص وتحسينها.
حافظ على تفاصيل القصة التي يذكرها المستخدم داخل المحادثة، ولا تغيّر أسماء الشخصيات أو قواعد العالم من دون طلبه.
كن صريحًا بشأن مواطن الضعف، وقدّم اقتراحات عملية ومحددة بدل المديح العام.
أجب بالعربية افتراضيًا، وباللهجة التي يطلبها المستخدم عند الحاجة. لا تدّعِ أنك قرأت ملفات أو فصولًا لم يرسلها المستخدم.
"""

PAGE = r"""<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#101018">
<title>MANOVEL AI</title>
<style>
:root{color-scheme:dark;--bg:#101018;--panel:#191923;--panel2:#20202c;--line:#30303d;--text:#f4f2fb;--muted:#a6a4b6;--accent:#a78bfa;--accent2:#7c3aed;--user:#29233c}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at top,#211a36 0,#101018 48%);color:var(--text);font-family:system-ui,-apple-system,"Segoe UI",Tahoma,sans-serif;min-height:100vh}
.app{max-width:1000px;margin:auto;min-height:100vh;display:flex;flex-direction:column;padding:0 20px}.top{height:78px;display:flex;align-items:center;gap:13px;border-bottom:1px solid #ffffff12}.logo{width:42px;height:42px;border-radius:14px;background:linear-gradient(140deg,#c4b5fd,#7c3aed);display:grid;place-items:center;color:#130d24;font-weight:900;font-size:19px;box-shadow:0 5px 25px #7c3aed35}.brand{font-size:18px;font-weight:800;letter-spacing:.4px}.brand small{display:block;font-size:11px;color:var(--muted);font-weight:500;letter-spacing:1.5px;margin-top:2px}.status{margin-right:auto;color:#a7f3d0;font-size:12px;display:flex;align-items:center;gap:7px}.dot{width:7px;height:7px;border-radius:100%;background:#34d399;box-shadow:0 0 10px #34d39988}
main{flex:1;display:flex;flex-direction:column;width:100%;max-width:820px;margin:0 auto;padding:30px 0 16px}.intro{text-align:center;margin:20px 0 30px}.intro h1{font-size:clamp(27px,5vw,42px);margin:0 0 12px;letter-spacing:-1px}.intro h1 span{color:var(--accent)}.intro p{margin:0;color:var(--muted);line-height:1.8;font-size:14px}.prompts{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin:0 0 22px}.chip{background:#ffffff08;border:1px solid var(--line);color:#e8e3f6;border-radius:14px;padding:13px 15px;text-align:right;cursor:pointer;font:inherit;font-size:13px;transition:.15s}.chip:hover{border-color:#8b5cf6;background:#8b5cf615}.chat{display:flex;flex-direction:column;gap:16px;padding-bottom:18px}.msg{max-width:88%;padding:14px 16px;border:1px solid var(--line);border-radius:17px;line-height:1.9;white-space:pre-wrap;overflow-wrap:anywhere;font-size:14px}.msg.assistant{align-self:flex-start;background:var(--panel);border-top-right-radius:5px}.msg.user{align-self:flex-end;background:var(--user);border-color:#66538a;border-top-left-radius:5px}.msg.error{border-color:#9f4848;color:#fecaca}.typing{display:none;color:var(--muted);font-size:12px;padding:4px 10px 12px}.typing.show{display:block}.composer{position:sticky;bottom:0;padding:12px 0 15px;background:linear-gradient(transparent,#101018 18%)}.formbox{display:flex;align-items:flex-end;gap:10px;background:#1b1b27;border:1px solid #454052;border-radius:18px;padding:10px;box-shadow:0 10px 40px #0003}.formbox:focus-within{border-color:#8b5cf6}textarea{flex:1;resize:vertical;min-height:48px;max-height:170px;border:0;outline:0;background:transparent;color:var(--text);font:inherit;font-size:14px;line-height:1.7;padding:10px 8px}textarea::placeholder{color:#858296}.send{flex:none;border:0;border-radius:13px;background:linear-gradient(135deg,#a78bfa,#7c3aed);color:white;padding:12px 18px;font:inherit;font-weight:750;cursor:pointer;min-width:78px}.send:disabled{opacity:.45;cursor:not-allowed}.note{text-align:center;color:#777487;font-size:11px;padding-top:10px}.reset{background:none;border:1px solid var(--line);color:var(--muted);border-radius:10px;padding:7px 10px;font:inherit;font-size:12px;cursor:pointer}.footrow{display:flex;align-items:center;gap:10px;justify-content:center}.empty-hide{display:none!important}
@media(max-width:600px){.app{padding:0 13px}.top{height:68px}.intro{margin:17px 0 23px}.prompts{grid-template-columns:1fr}.chip{padding:11px 13px}.msg{max-width:96%}.send{padding:12px 13px;min-width:66px}.formbox{gap:6px;padding:7px}.status{font-size:11px}}
</style>
</head>
<body>
<div class="app">
<header class="top">
  <div class="logo">M</div><div class="brand">MANOVEL AI<small>YOUR STORY. YOUR WORLD.</small></div>
  <div class="status"><span class="dot"></span> جاهز للمحادثة</div>
</header>
<main>
  <section class="intro" id="intro">
    <h1>خلّينا نبني <span>عالمك</span></h1>
    <p>مساعدك في كتابة الروايات والمانهوا وتطوير الشخصيات والحبكات<br>ابدأ بفكرة، أو اسأل عن مشهد تعمل عليه.</p>
  </section>
  <section class="prompts" id="prompts">
    <button class="chip" data-prompt="ساعدني أبني شخصية رئيسية عميقة ومتعددة الطبقات">✦ بناء شخصية عميقة</button>
    <button class="chip" data-prompt="اقترح حبكة غير متوقعة لرواية فانتازيا مظلمة">✦ حبكة لفانتازيا مظلمة</button>
    <button class="chip" data-prompt="راجع هذه الفكرة نقديًا واذكر نقاط قوتها وضعفها">✦ نقد فكرة روائية</button>
    <button class="chip" data-prompt="ساعدني أكتب مشهدًا مؤثرًا بحوار طبيعي ووصف قوي">✦ كتابة مشهد مؤثر</button>
  </section>
  <section class="chat" id="chat" aria-live="polite"></section>
  <div class="typing" id="typing">MANOVEL AI يكتب الآن…</div>
  <section class="composer">
    <form id="form" class="formbox">
      <textarea id="message" rows="1" maxlength="10000" placeholder="اكتب فكرتك أو سؤالك هنا…" aria-label="رسالتك"></textarea>
      <button class="send" id="send" type="submit">إرسال ↑</button>
    </form>
    <div class="note footrow"><span>تحقّق من المعلومات المهمة واحتفظ بنسخة من أفكارك</span><button class="reset" id="reset" type="button">محادثة جديدة</button></div>
  </section>
</main>
</div>
<script>
const chat = document.getElementById('chat');
const form = document.getElementById('form');
const input = document.getElementById('message');
const send = document.getElementById('send');
const typing = document.getElementById('typing');
const intro = document.getElementById('intro');
const prompts = document.getElementById('prompts');
let history = [];
let busy = false;
function addMessage(role, text, error=false) {
  const el = document.createElement('div');
  el.className = 'msg ' + (role === 'user' ? 'user' : 'assistant') + (error ? ' error' : '');
  el.textContent = text;
  chat.appendChild(el);
  el.scrollIntoView({behavior:'smooth', block:'end'});
  return el;
}
function startPrompt(value) { input.value = value; input.focus(); input.style.height='auto'; input.style.height=Math.min(input.scrollHeight,170)+'px'; }
document.querySelectorAll('[data-prompt]').forEach(button => button.addEventListener('click', () => startPrompt(button.dataset.prompt)));
input.addEventListener('input', () => { input.style.height='auto'; input.style.height=Math.min(input.scrollHeight,170)+'px'; });
form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const message = input.value.trim();
  if (!message || busy) return;
  const previousHistory = history.slice(-10);
  history.push({role:'user', text:message});
  addMessage('user', message);
  intro.classList.add('empty-hide'); prompts.classList.add('empty-hide');
  input.value=''; input.style.height='auto'; busy=true; send.disabled=true; typing.classList.add('show');
  try {
    const res = await fetch('/chat', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({message, history:previousHistory})});
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'تعذّر إكمال الطلب.');
    const reply = data.reply || 'لم يصل رد نصي.';
    addMessage('assistant', reply);
    history.push({role:'model', text:reply});
