
import os
from flask import Flask, request, jsonify, render_template_string
from google import genai

app = Flask(__name__)

api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

SYSTEM_PROMPT = """
أنت MANOVEL AI، مساعد متخصص في تحليل الروايات والمانجا والمانهوا
والأنمي، خصوصًا تحليل قوة الشخصيات ومقارنتها.

عند تحليل القوة، افحص الأدلة المعروضة داخل العمل، ومنها:
- القوة التدميرية والإنجازات الفعلية
- السرعة وردود الفعل
- التحمل والمتانة والقدرة على الاستمرار
- القدرات الخاصة والحيل القتالية (Hax)
- المدى، نقاط الضعف، وشروط استخدام القدرات
- السياق، اختلاف النسخ، وموثوقية الأدلة

لا تخترع إنجازات أو معلومات غير مؤكدة.
ميّز بين الحقائق والاستنتاجات والافتراضات.
لا تفترض أن الشخصية الأقوى في جانب واحد ستفوز دائمًا.
أجب باللغة التي يستخدمها السائل، وكن واضحًا ومنصفًا.
"""

WELCOME = """
أهلًا بك في MANOVEL AI!
أنا مساعدك لتحليل الشخصيات والمانجا والمانهوا والروايات،
ومقارنة الإنجازات والسرعة والتحمل والقدرات الخاصة.
المحادثة غير محفوظة بشكل دائم على هذا الخادم.
"""

PAGE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MANOVEL AI</title>
<style>
body{font-family:Arial,sans-serif;background:#101014;color:#f5f5f5;
max-width:800px;margin:35px auto;padding:16px}
h1{color:#b69cff}
#chat{background:#191920;border:1px solid #353541;border-radius:12px;
padding:16px;min-height:220px;white-space:pre-wrap}
textarea{box-sizing:border-box;width:100%;margin-top:12px;padding:12px;
background:#191920;color:white;border:1px solid #555;border-radius:8px}
button{padding:12px 20px;margin-top:8px;cursor:pointer}
</style>
</head>
<body>
<h1>أهلًا بك في MANOVEL AI</h1>
<p>تحليل الشخصيات والإنجازات ومقارنة القوة والسرعة والتحمل والقدرات الخاصة.</p>
<div id="chat">{{ welcome }}</div>
<textarea id="message" rows="3" placeholder="اكتب سؤالك هنا..."></textarea>
<button id="send" onclick="sendMessage()">إرسال</button>
<script>
async function sendMessage(){
 const box=document.getElementById('message');
 const chat=document.getElementById('chat');
 const button=document.getElementById('send');
 const message=box.value.trim();
 if(!message)return;
 chat.textContent += '\\n\\nأنت: '+message+'\\n\\nMANOVEL AI: جارٍ التفكير...';
 box.value='';
 button.disabled=true;
 try{
  const r=await fetch('/chat',{method:'POST',
   headers:{'Content-Type':'application/json'},
   body:JSON.stringify({message})});
  const data=await r.json();
  chat.textContent += '\\n'+(data.reply||data.error||'حدث خطأ.');
 }catch(e){chat.textContent+='\\nتعذر الاتصال بالخادم.';}
 finally{button.disabled=false;}
}
</script>
</body>
</html>
"""

@app.get("/")
def home():
    return render_template_string(PAGE, welcome=WELCOME)

@app.post("/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()

    if not message:
        return jsonify({"error": "اكتب سؤالك أولًا."}), 400

    if not client:
        return jsonify({"error": "لم يتم إعداد GEMINI_API_KEY في Render."}), 500

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=SYSTEM_PROMPT + "\n\nسؤال المستخدم:\n" + message
        )
        return jsonify({"reply": response.text or "لم يصل رد نصي."})
    except Exception:
        
    app.logger.exception("Gemini request failed")
    return jsonify({"error": "حدث خطأ في الاتصال بالذكاء الاصطناعي. تحقق من إعدادات Render والمفتاح."}), 500
 
from workers import wsgi

Default = wsgi.entrypoint(app)
