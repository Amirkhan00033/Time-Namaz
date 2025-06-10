import os

def show_notification(title, message):
    os.system(f'''
              osascript -e 'display notification "{message}" with title "{title}"'
              ''')

show_notification("🕌 Время Намаза", "Пора готовиться к намазу, брат!")

