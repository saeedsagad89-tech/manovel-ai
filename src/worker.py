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
  } catch (err) {
    const msg = err && err.message ? err.message : 'تعذر الاتصال. حاول مرة أخرى.';
    addMessage('assistant', msg, true);
    history.pop();
  } finally {
    busy=false; send.disabled=false; typing.classList.remove('show'); input.focus();
  }
});
document.getElementById('reset').addEventListener('click', () => {
  history=[]; chat.replaceChildren(); intro.classList.remove('empty-hide'); prompts.classList.remove('empty-hide'); input.value=''; input.style.height='auto'; input.focus();
});
</script>
</body>
</html>"""


def json_response(data, status=200):
    return Response(
        json.dumps(data, ensure_ascii=False),
        status=status,
        headers={"Content-Type": "application/json; charset=utf-8"},
    )


def js_object(value):
    return to_js(value, dict_converter=Object.fromEntries)


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        method = str(request.method).upper()
        path = urlparse(str(request.url)).path

        if method == "GET" and path == "/":
            return Response(
                PAGE,
                headers={"Content-Type": "text/html; charset=utf-8"},
            )

        if method == "GET" and path == "/health":
            return json_response({"ok": True, "app": "MANOVEL AI"})

        if path == "/chat" and method == "POST":
            try:
                incoming = await request.json()
            except Exception:
                return json_response({"error": "تعذر قراءة الرسالة. حاول مرة أخرى."}, 400)

            message = str(incoming.get("message", "")).strip()
            if not message:
                return json_response({"error": "اكتب رسالتك أولًا."}, 400)
            if len(message) > 10000:
                return json_response({"error": "الرسالة طويلة جدًا. اختصرها قليلًا."}, 413)

            api_key = getattr(self.env, "GEMINI_API_KEY", None)
            if not api_key:
                return json_response(
                    {"error": "مفتاح Gemini غير مضبوط بعد. أضف GEMINI_API_KEY في Cloudflare Secrets."},
                    500,
                )

            history = incoming.get("history", [])
            contents = []
            if isinstance(history, list):
                for item in history[-10:]:
                    if not isinstance(item, dict):
                        continue
                    role = item.get("role")
                    text = str(item.get("text", "")).strip()
                    if role in ("user", "model") and text:
                        contents.append({"role": role, "parts": [{"text": text[:10000]}]})
            contents.append({"role": "user", "parts": [{"text": message}]})

            payload = {
                "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
                "contents": contents,
                "generationConfig": {"temperature": 0.8, "maxOutputTokens": 4096},
            }
            options = js_object({
                "method": "POST",
                "headers": {
                    "Content-Type": "application/json",
                    "x-goog-api-key": str(api_key),
                },
                "body": json.dumps(payload, ensure_ascii=False),
            })

            try:
                upstream = await fetch(
                    f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent",
                    options,
                )
                raw = str(await upstream.text())
                try:
                    result = json.loads(raw)
                except Exception:
