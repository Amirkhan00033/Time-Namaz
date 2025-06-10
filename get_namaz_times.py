import requests
import datetime

city = "Almaty"
country = "Kazakhstan"
method = 2  # метод расчёта (2 = ISNA)

# Получаем сегодняшнюю дату
today = datetime.datetime.now().strftime("%d-%m-%Y")

# Запрос к API
url = f"http://api.aladhan.com/v1/timingsByCity?city={city}&country={country}&method={method}&date={today}"

response = requests.get(url)
data = response.json()

if data["code"] == 200:
    timings = data["data"]["timings"]
    print("🕌 Время намаза на сегодня:")
    for prayer, time in timings.items():
        print(f"{prayer}: {time}")
else:
    print("❌ Ошибка получения данных:", data["status"])
