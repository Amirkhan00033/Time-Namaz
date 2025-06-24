from flask import Flask, render_template_string
from datetime import datetime, timedelta
import pytz
import requests

app = Flask(__name__)

# Настройки для API: можно менять method и tune, чтобы подгонять времена
LATITUDE = 43.238949
LONGITUDE = 76.889709
METHOD = 99  # Попробуй 2, 4, 7, 8, 9, 99 и смотри, что ближе к твоему расписанию
SCHOOL = 1   # 0 — Шафии, 1 — Ханбали/Ханафи
# tune — 7 чисел: Imsak,Fajr,Sunrise,Dhuhr,Asr,Maghrib,Isha (в минутах)
TUNE = "-5,0,4,3,4,3,0,0,0,0,0"  # Пример сдвигов, подгоняй под себя

def get_namaz_times():
    url = "https://api.aladhan.com/v1/timings"
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "method": METHOD,
        "school": SCHOOL,
        "tune": TUNE
    }
    resp = requests.get(url, params=params)
    data = resp.json()["data"]
    timings = data["timings"]
    tz = pytz.timezone(data["meta"]["timezone"])

    now = datetime.now(tz)
    res = {}
    # Берём только нужные нам времена
    for name in ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]:
        h, m = map(int, timings[name].split(":"))
        dt = now.replace(hour=h, minute=m, second=0, microsecond=0)
        res[name] = dt
    return res

def get_next_and_left(times, now):
    sorted_times = sorted(times.items(), key=lambda x: x[1])
    for name, dt in sorted_times:
        if dt > now:
            diff = dt - now
            return name, diff.seconds // 3600, (diff.seconds % 3600) // 60
    # Если все времена прошли — следующий на следующий день
    name, dt = sorted_times[0]
    diff = dt + timedelta(days=1) - now
    return name, diff.seconds // 3600, (diff.seconds % 3600) // 60

@app.route("/")
def home():
    times = get_namaz_times()
    tz = pytz.timezone("Asia/Almaty")
    now = datetime.now(tz)
    now_str = now.strftime("%H:%M:%S")
    next_prayer, hrs_left, mins_left = get_next_and_left(times, now)
    times_str = {k: v.strftime("%H:%M") for k, v in times.items()}

    html = """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="utf-8" />
        <title>🕌 Намаз — Almaty</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <style>
            body { font-family: Arial, sans-serif; background: #e6f0ff; color: #003366; padding: 20px; }
            h1 { text-align: center; }
            #now, #next { text-align: center; margin: 10px 0; font-size: 18px; }
            ul { list-style: none; padding: 0; max-width: 300px; margin: auto; }
            li { padding: 6px; border-radius: 6px; font-size: 20px; }
            .cur { background: #d0f0c0; font-weight: bold; color: #2e7d32; }
            #toggle { display: block; margin: 15px auto; padding: 10px 20px; background: #003366; color: #fff; border: none; border-radius: 6px; cursor: pointer; }
            .footer { text-align: center; color: #555; font-size: 14px; margin-top: 20px; }
        </style>
    </head>
    <body>
        <h1>🕌 Намаз — Almaty</h1>
        <div id="now">Сейчас: {{ now_str }}</div>
        <div id="next">Следующий: <b>{{ next_prayer }}</b> через {{ hrs_left }} ч {{ mins_left }} мин</div>
        <ul id="list">
        {% for name, time in times_str.items() %}
            <li data-name="{{ name }}">
            {% if name == "Fajr" %}🌙{% elif name == "Sunrise" %}🌅{% elif name == "Dhuhr" %}☀️
            {% elif name == "Asr" %}🌇{% elif name == "Maghrib" %}🌆{% elif name == "Isha" %}🌃{% endif %}
            {{ name }}: {{ time }}
            </li>
        {% endfor %}
        </ul>
        <button id="toggle">Включить уведомления</button>
        <div class="footer">Обнови страницу для актуализации</div>

        <script>
            const T = {{ times_str | tojson }};
            let notificationsOn = false;

            document.getElementById('toggle').onclick = async function () {
                if (Notification.permission !== 'granted') {
                    await Notification.requestPermission();
                }
                notificationsOn = !notificationsOn;
                this.textContent = notificationsOn ? 'Выключить уведомления' : 'Включить уведомления';
            };

            const Mets = Object.fromEntries(Object.entries(T).map(([name, time]) => {
                const [h, m] = time.split(':').map(Number);
                return [name, h * 60 + m];
            }));

            function update() {
                const d = new Date();
                const cm = d.getHours() * 60 + d.getMinutes();
                let currentPrayer = Object.keys(Mets)[0];
                for (const [name, val] of Object.entries(Mets)) {
                    if (val <= cm) currentPrayer = name;
                }
                if (cm < Math.min(...Object.values(Mets))) currentPrayer = Object.keys(Mets).pop();

                document.querySelectorAll('#list li').forEach(li => {
                    li.classList.toggle('cur', li.dataset.name === currentPrayer);
                });

                document.getElementById('now').textContent = 'Сейчас: ' + d.toTimeString().slice(0, 8);

                if (notificationsOn) {
                    const mm = ('0' + d.getMinutes()).slice(-2);
                    const hh = d.getHours();
                    const currentTime = `${hh}:${mm}`;
                    for (const [name, time] of Object.entries(T)) {
                        if (time === currentTime) {
                            new Notification('🕌 Намаз', { body: name });
                        }
                    }
                }
            }

            setInterval(update, 1000);
            window.onload = update;
        </script>
    </body>
    </html>
    """
    return render_template_string(html, now_str=now_str, next_prayer=next_prayer, hrs_left=hrs_left, mins_left=mins_left, times_str=times_str)

if __name__ == "__main__":
    app.run(debug=True)
