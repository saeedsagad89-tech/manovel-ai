@app.get("/")
def home():
    return """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>MANOVEL AI</title>
        <style>
            body {
                margin: 0;
                min-height: 100vh;
                display: grid;
                place-items: center;
                background: #101014;
                color: #f5f5f5;
                font-family: Arial, sans-serif;
                text-align: center;
            }
            .welcome {
                max-width: 600px;
                margin: 24px;
                padding: 32px;
                border: 1px solid #353541;
                border-radius: 18px;
                background: #191920;
            }
            h1 { color: #b69cff; }
            p { line-height: 1.9; }
            .notice { color: #ffc978; }
        </style>
    </head>
    <body>
        <main class="welcome">
            <h1>أهلًا بك في MANOVEL AI</h1>
            <p>
                وجهتك لنقاش الأنمي والمانغا والمانهوا والروايات،
                وتحليل الشخصيات والقوى والإنجازات ومقارنة مستويات القوة.
            </p>
            <p class="notice">
                تنبيه: قد تُمحى المحادثة عند مغادرة الصفحة،
                لذلك لا تعتمد على حفظ سجل المحادثات.
            </p>
        </main>
    </body>
    </html>
    """
