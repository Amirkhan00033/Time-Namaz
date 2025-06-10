# Импортируем нужные библиотеки
import requests  # для отправки запроса на сайт Aladhan
from datetime import datetime  # для работы с датой и временем (пока не используется)
import tkinter as tk  # для создания GUI (окна приложения)
from tkinter import messagebox  # для вывода сообщений об ошибке

# 🕌 Функция, которая получает время намаза с сайта Aladhan
def get_namaz_times():
    city = "Almaty"         # Город
    country = "Kazakhstan"  # Страна
    method = 99             # Кастомный метод (чтобы использовать свои настройки времени)
    school = 1              # Ханафитская школа фикха
    tune = "0,-3,3,77,3,3,1,0,0,0,0"  # Настройка времени (в минутах) для каждого намаза

    # Ссылка на API с параметрами
    url = f"https://api.aladhan.com/v1/timingsByCity?city={city}&country={country}&method={method}&school={school}&tune={tune}"
    
    try:
        # Отправляем GET-запрос на сайт
        response = requests.get(url)

        # Преобразуем ответ в формат JSON (словарь Python)
        data = response.json()

        # Получаем нужное поле "timings", где хранятся времена намаза
        timings = data["data"]["timings"]

        # Возвращаем только нужные намаз-времена (Fajr, Sunrise, и т.д.)
        return {
            "Fajr": timings["Fajr"],
            "Sunrise": timings["Sunrise"],
            "Dhuhr": timings["Dhuhr"],
            "Asr": timings["Asr"],
            "Maghrib": timings["Maghrib"],
            "Isha": timings["Isha"]
        }
    except Exception as e:
        # Если возникла ошибка (например, нет интернета) — вывести ошибку в консоль
        print("Ошибка:", e)
        return None  # Возвращаем пусто, чтобы обработать ошибку в GUI

# 📱 Функция для отображения времени намаза на экране
def show_namaz_times():
    timings = get_namaz_times()  # Получаем времена намаза
    if timings:
        # Формируем красивый текст для отображения
        result = "\n".join([f"{key}: {value}" for key, value in timings.items()])
        # Устанавливаем текст в лейбл
        label.config(text=f"🕌 Время намаза на сегодня:\n\n{result}")
    else:
        # Показываем окно с ошибкой, если не удалось загрузить данные
        messagebox.showerror("Ошибка", "Не удалось получить время намаза.")

# 🖼️ Создаём основное окно приложения
root = tk.Tk()
root.title("Время Намаза — Almaty")  # Заголовок окна
root.geometry("300x300")             # Размер окна
root.resizable(False, False)         # Запрещаем изменение размера

# 📋 Надпись, куда будем выводить время намаза
label = tk.Label(
    root,
    text="Загрузка...",              # Текст при запуске
    font=("Helvetica", 12),          # Шрифт
    justify="left",                  # Выравнивание текста по левому краю
    padx=10, pady=10                 # Отступы
)
label.pack()  # Отображаем лейбл

# 🔁 Кнопка "Обновить", чтобы вручную перезагрузить время
button = tk.Button(
    root,
    text="Обновить",                 # Надпись на кнопке
    command=show_namaz_times,        # Что произойдёт при нажатии
    font=("Helvetica", 10)
)
button.pack(pady=10)  # Отступ снизу

# 📥 Загружаем время при запуске приложения
show_namaz_times()

# 🔁 Запускаем главное окно приложения (вечный цикл)
root.mainloop()
