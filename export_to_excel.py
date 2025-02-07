import pandas as pd
from datetime import datetime

# Путь к Excel файлу для хранения данных
EXCEL_FILE = 'users_data.xlsx'

# Функция для проверки существования файла и создания его, если он не существует
def create_excel_file():
    try:
        # Проверяем, существует ли файл
        df = pd.read_excel(EXCEL_FILE)
    except FileNotFoundError:
        # Если файл не найден, создаем новый
        df = pd.DataFrame(columns=["id", "username", "id_discord", "level", "experience", "money", "registration_date", "points"])
        df.to_excel(EXCEL_FILE, index=False)
        print("Создан новый файл Excel.")

# Функция для добавления пользователя в Excel
def add_user_to_excel(username: str):
    print(f"Попытка добавить пользователя {username} в базу данных Excel.")  # Логируем начало добавления
    try:
        # Проверяем, существует ли файл
        df = pd.read_excel(EXCEL_FILE)
    except FileNotFoundError:
        create_excel_file()
        df = pd.read_excel(EXCEL_FILE)
    
    # Проверяем, существует ли уже пользователь в базе
    if username not in df['username'].values:
        new_user = {
            "id": len(df) + 1,  # Уникальный ID
            "username": username,
            "id_discord": "",  # Пустое поле для Discord ID
            "level": 1,
            "experience": 0,
            "money": 0,
            "registration_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "points": 0
        }
        # Используем pd.concat вместо append
        new_user_df = pd.DataFrame([new_user])  # Преобразуем новый пользователь в DataFrame
        df = pd.concat([df, new_user_df], ignore_index=True)  # Объединяем с основным DataFrame
        df.to_excel(EXCEL_FILE, index=False)
        print(f"Пользователь {username} успешно добавлен в базу данных Excel.")  # Логируем успешное добавление
    else:
        print(f"Пользователь {username} уже существует в базе данных.")

# Пример вызова функции
add_user_to_excel("NewUser")





