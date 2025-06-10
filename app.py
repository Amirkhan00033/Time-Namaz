from flask import Flask, render_template_string
from datetime import datetime, time
import pytz

app = Flask(__name__)

def get_namaz_times():
    tz = pytz.timezone("Asia/Almaty")
    today = datetime.now(tz).date()

    fixed_times = {
        "Fajr": "02:24",
        "Sunrise": "04:09",
        "Dhuhr": "11:55",
        "Asr": "17:14",
        "Maghrib": "19:35",
        "Isha": "21:20"
    }

    result = {}
    for name, time_str in fixed_times.items():
        hour, minute = map(int, time_str.split(":"))
        dt = datetime.combine(today, time(hour, minute))
        dt = tz.localize(dt)
        result[name] = dt.strftime("%H:%M")

    return result

@app.route("/")
def home():
    timings = get_namaz_times()
    tz = pytz.timezone("Asia/Almaty")
    now = datetime.now(tz).strftime("%H:%M:%S")

    html = """
    <html>
    <head>
        <title>Время Намаза — Almaty</title>
        <style>
            body { font-family: Arial, sans-serif; background: #e6f0ff; color: #003366; padding: 20px; }
            h1 { text-align: center; }
            ul { list-style-type: none; padding: 0; max-width: 300px; margin: auto; }
            li { padding: 8px 0; font-size: 20px; }
            .prayer { font-weight: bold; }
            .footer { text-align: center; margin-top: 30px; font-size: 14px; color: #555; }
            #current-time { text-align: center; font-size: 18px; margin-bottom: 20px; }
        </style>
        <script>
            // Функция обновления времени на странице каждую секунду
            function updateTime() {
                const now = new Date();
                const hours = String(now.getHours()).padStart(2, '0');
                const minutes = String(now.getMinutes()).padStart(2, '0');
                const seconds = String(now.getSeconds()).padStart(2, '0');
                document.getElementById('current-time').textContent = 'Текущее время: ' + hours + ':' + minutes + ':' + seconds;
            }

            // Запускаем обновление каждую секунду
            setInterval(updateTime, 1000);

            // Запуск сразу при загрузке страницы
            window.onload = updateTime;
        </script>
    </head>
    <body>
        <h1>🕌 Время намаза — Almaty</h1>
        <div id="current-time">Текущее время: {{ now }}</div>
        <ul>
            <li>🌙 <span class="prayer">Фаджр:</span> {{ timings["Fajr"] }}</li>
            <li>🌅 <span class="prayer">Восход:</span> {{ timings["Sunrise"] }}</li>
            <li>☀️ <span class="prayer">Зухр:</span> {{ timings["Dhuhr"] }}</li>
            <li>🌇 <span class="prayer">Аср:</span> {{ timings["Asr"] }}</li>
            <li>🌆 <span class="prayer">Магриб:</span> {{ timings["Maghrib"] }}</li>
            <li>🌃 <span class="prayer">Иша:</span> {{ timings["Isha"] }}</li>
        </ul>
        <div class="footer">Обнови страницу для обновления времени намаза</div>
    </body>
    </html>
    """
    return render_template_string(html, timings=timings, now=now)

if __name__ == "__main__":
    app.run(debug=True)
