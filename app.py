from flask import Flask, render_template_string, send_from_directory
from datetime import datetime, time, timedelta
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
        result[name] = dt

    return result

def get_next_prayer_and_time_left(namaz_datetimes, now):
    sorted_prayers = sorted(namaz_datetimes.items(), key=lambda x: x[1])
    for name, dt in sorted_prayers:
        if dt > now:
            next_prayer = name
            diff = dt - now
            break
    else:
        # Если все намазы уже прошли — следующий завтра (первый + 1 день)
        name, dt = sorted_prayers[0]
        next_prayer = name
        diff = dt + timedelta(days=1) - now

    hours, remainder = divmod(diff.seconds, 3600)
    minutes = remainder // 60

    return next_prayer, hours, minutes

def get_current_prayer(namaz_datetimes, now):
    """
    Определяем текущий намаз, то есть последний, время которого уже прошло, но следующий ещё не наступил.
    Например, если сейчас между Зухр и Аср — текущий намаз Зухр.
    """
    sorted_prayers = sorted(namaz_datetimes.items(), key=lambda x: x[1])

    current = None
    for i, (name, dt) in enumerate(sorted_prayers):
        if dt > now:
            # Намаз, который сейчас идёт — это предыдущий из списка
            current = sorted_prayers[i-1][0] if i > 0 else sorted_prayers[-1][0]
            break
    else:
        # Если сейчас после последнего намаза — значит сейчас последний намаз (Иша)
        current = sorted_prayers[-1][0]

    return current

@app.route("/")
def home():
    timings = get_namaz_times()
    tz = pytz.timezone("Asia/Almaty")
    now_dt = datetime.now(tz)
    now_str = now_dt.strftime("%H:%M:%S")

    next_prayer, hours_left, minutes_left = get_next_prayer_and_time_left(timings, now_dt)
    # current_prayer теперь не нужен для подсветки на сервере, так как подсветка будет JS
    #current_prayer = get_current_prayer(timings, now_dt)

    timings_str = {k: v.strftime("%H:%M") for k, v in timings.items()}

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
            .prayer { font-weight: normal; padding: 4px 8px; border-radius: 8px; }
            .current { 
                background-color: #d0f0c0; /* светло-зеленый */
                font-weight: bold;
                color: #2e7d32; /* темно-зеленый текст */
            }
            .footer { text-align: center; margin-top: 30px; font-size: 14px; color: #555; }
            #current-time { text-align: center; font-size: 18px; margin-bottom: 20px; }
            #notif-toggle { display: block; margin: 20px auto; padding: 10px 20px; background: #003366; color: white; border: none; border-radius: 8px; cursor: pointer; }
            #next-prayer-info { text-align: center; font-size: 18px; margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <h1>🕌 Время намаза — Almaty</h1>
        <div id="current-time">Текущее время: {{ now }}</div>
        <div id="next-prayer-info">
            Следующий намаз: <strong>{{ next_prayer }}</strong> через {{ hours_left }} часов {{ minutes_left }} минут
        </div>
        <ul id="prayer-list">
            {% for name, time in timings.items() %}
                <li class="prayer" data-name="{{ name }}">
                    {% if name == "Fajr" %}🌙{% elif name == "Sunrise" %}🌅{% elif name == "Dhuhr" %}☀️{% elif name == "Asr" %}🌇{% elif name == "Maghrib" %}🌆{% elif name == "Isha" %}🌃{% endif %}
                    <span class="prayer-name">{{ name }}:</span> {{ time }}
                </li>
            {% endfor %}
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

            function timeToMinutes(t) {
                const [h, m] = t.split(":").map(Number);
                return h * 60 + m;
            }

            const namazTimesMinutes = {};
            for (const [name, t] of Object.entries(namazTimes)) {
                namazTimesMinutes[name] = timeToMinutes(t);
            }

            
                   function updateCurrentPrayerHighlight() {
    const now = new Date();
    const currentMinutes = now.getHours() * 60 + now.getMinutes();

    const sortedPrayers = Object.entries(namazTimesMinutes).sort((a,b) => a[1] - b[1]);

    // Найдём текущий намаз - последний, у которого время <= currentMinutes
    // Если текущее время меньше времени первого намаза (например, 02:00 < 02:24),
    // значит текущий намаз - последний из предыдущего дня (Иша)
    let currentPrayer = sortedPrayers[0][0];
    for (let i = 0; i < sortedPrayers.length; i++) {
        if (sortedPrayers[i][1] <= currentMinutes) {
            currentPrayer = sortedPrayers[i][0];
        }
    }
    if (currentMinutes < sortedPrayers[0][1]) {
        // Текущий намаз последний из списка (Иша)
        currentPrayer = sortedPrayers[sortedPrayers.length - 1][0];
    }

    document.querySelectorAll("#prayer-list li.prayer").forEach(li => {
        li.classList.remove("current");
        // Убираем стрелочку из span с классом arrow, если есть
        const arrowSpan = li.querySelector(".arrow");
        if (arrowSpan) {
            arrowSpan.remove();
        }
        if (li.dataset.name === currentPrayer) {
            li.classList.add("current");
            // Добавим стрелочку в начало li, не ломая эмодзи и текст
            const arrow = document.createElement("span");
            arrow.textContent = "▶️ ";
            arrow.classList.add("arrow");
            li.prepend(arrow);
        }
    });
}
 

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

            setInterval(() => {
                updateCurrentPrayerHighlight();
                updateTime();
            }, 1000);

            window.onload = () => {
                updateCurrentPrayerHighlight();
                updateTime();
            };

            if ('serviceWorker' in navigator) {
                navigator.serviceWorker.register('/static/sw.js')
                    .then(() => console.log("✅ Service Worker зарегистрирован"))
                    .catch(err => console.error("❌ SW ошибка:", err));
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html, timings=timings_str, now=now_str, 
                                  next_prayer=next_prayer, hours_left=hours_left, minutes_left=minutes_left)


@app.route('/manifest.json')
def manifest():
    return send_from_directory(os.path.dirname(__file__), 'manifest.json')

if __name__ == "__main__":
    app.run(debug=True)
