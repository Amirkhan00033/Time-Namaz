import requests
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox

def get_namaz_times():
    # Точное время, как ты прислал (можно потом заменить на API)
    # Формат "ЧЧ:ММ"
    return {
        "Fajr": "02:24",
        "Sunrise": "04:09",
        "Dhuhr": "11:55",
        "Asr": "17:14",
        "Maghrib": "19:36",
        "Isha": "21:21"
    }

def get_next_prayer(timings):
    now = datetime.now()
    for name, time_str in timings.items():
        prayer_time = datetime.strptime(time_str, "%H:%M").replace(
            year=now.year, month=now.month, day=now.day
        )
        if now < prayer_time:
            return name, prayer_time
    # Если все намазы уже прошли сегодня, следующий - Фаджр завтра
    fajr_time = datetime.strptime(timings["Fajr"], "%H:%M").replace(
        year=now.year, month=now.month, day=now.day
    ) + timedelta(days=1)
    return "Fajr", fajr_time

def time_until(next_time):
    now = datetime.now()
    diff = next_time - now
    if diff.total_seconds() < 0:
        diff += timedelta(days=1)
    hours = diff.seconds // 3600
    minutes = (diff.seconds % 3600) // 60
    return hours, minutes

def show_namaz_times():
    timings = get_namaz_times()
    if timings:
        next_name, next_time = get_next_prayer(timings)
        hours, minutes = time_until(next_time)

        icons = {
            "Fajr": "🌙",
            "Sunrise": "🌅",
            "Dhuhr": "☀️",
            "Asr": "🌇",
            "Maghrib": "🌆",
            "Isha": "🌃"
        }

        result = ""
        for name, time in timings.items():
            line = f"{icons.get(name, '')} {name}: {time}"
            if name == next_name:
                line += " ← следующий"
            result += line + "\n"

        current_time = datetime.now().strftime("%H:%M:%S")
        time_left_str = f"Осталось до следующего намаза: {hours} ч {minutes} мин"
        label.config(
            text=f"🕌 Время намаза — Almaty\n\n⏰ Сейчас: {current_time}\n{time_left_str}\n\n{result}"
        )
    else:
        messagebox.showerror("Ошибка", "Не удалось получить время намаза.")
    
    # Автообновление каждые 30 секунд (30000 миллисекунд)
    root.after(30000, show_namaz_times)

root = tk.Tk()
root.title("🕌 Namaz Times — Almaty")
root.geometry("350x400")
root.resizable(False, False)

# Цвет фона
root.configure(bg="#e6f0ff")  # мягкий голубой фон

label = tk.Label(
    root,
    text="Загрузка...",
    font=("Segoe UI", 13),
    bg="#e6f0ff",
    fg="#003366",  # темно-синий текст
    justify="left",
    padx=15,
    pady=15
)
label.pack()

button = tk.Button(
    root,
    text="🔄 Обновить",
    command=show_namaz_times,
    font=("Segoe UI", 12, "bold"),
    bg="#007acc",
    fg="white",
    activebackground="#005a9e",
    activeforeground="white",
    relief="flat",
    padx=15,
    pady=8,
    bd=0,
)
button.pack(pady=20)

show_namaz_times()  # Запускаем первый показ и автообновление
root.mainloop()
