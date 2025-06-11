from flask import Flask, render_template_string, send_from_directory
from datetime import datetime, time
import pytz
import os

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
        <link rel="manifest" href="/manifest.json">
        <meta name="theme-color" content="#003366">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: Arial, sans-serif; background: #e6f0ff; color: #003366; padding: 20px; }
            h1 { text-align: center; }
            ul { list-style-type: none; padding: 0; max-width: 300px; margin: auto; }
            li { padding: 8px 0; font-size: 20px; }
            .prayer { font-weight: bold; }
            .footer { text-align: center; margin-top: 30px; font-size: 14px; color: #555; }
            #current-time { text-align: center; font-size: 18px; margin-bottom: 20px; }
            #notif-toggle { display: block; margin: 20px auto; padding: 10px 20px; background: #003366; color: white; border: none; border-radius: 8px; cursor: pointer; }
        </style>
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

        <button id="notif-toggle">Включить уведомления</button>
        <div class="footer">Обнови страницу для обновления времени намаза</div>

        <script>
            const namazTimes = {
                Fajr: "{{ timings['Fajr'] }}",
                Sunrise: "{{ timings['Sunrise'] }}",
                Dhuhr: "{{ timings['Dhuhr'] }}",
                Asr: "{{ timings['Asr'] }}",
                Maghrib: "{{ timings['Maghrib'] }}",
                Isha: "{{ timings['Isha'] }}"
            };

            let notificationsEnabled = false;

            document.getElementById("notif-toggle").addEventListener("click", async () => {
                if (Notification.permission !== "granted") {
                    await Notification.requestPermission();
                }

                notificationsEnabled = !notificationsEnabled;
                document.getElementById("notif-toggle").textContent = notificationsEnabled ? "Выключить уведомления" : "Включить уведомления";
            });

            function updateTime() {
                const now = new Date();
                const hours = String(now.getHours()).padStart(2, '0');
                const minutes = String(now.getMinutes()).padStart(2, '0');
                const seconds = String(now.getSeconds()).padStart(2, '0');
                document.getElementById('current-time').textContent = 'Текущее время: ' + hours + ':' + minutes + ':' + seconds;

                const currentTime = hours + ":" + minutes;

                if (notificationsEnabled) {
                    for (const [name, time] of Object.entries(namazTimes)) {
                        if (time === currentTime) {
                            new Notification("🕌 Время намаза", {
                                body: `${name} — сейчас время намаза`,
                                icon: "/static/icons/icon-192.png"
                            });
                        }
                    }
                }
            }

            setInterval(updateTime, 1000);
            window.onload = updateTime;

            if ('serviceWorker' in navigator) {
                navigator.serviceWorker.register('/static/sw.js')
                    .then(() => console.log("✅ Service Worker зарегистрирован"))
                    .catch(err => console.error("❌ SW ошибка:", err));
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html, timings=timings, now=now)

@app.route('/manifest.json')
def manifest():
    return send_from_directory(os.path.dirname(__file__), 'manifest.json')

if __name__ == "__main__":
    app.run(debug=True)
