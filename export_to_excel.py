import sqlite3
import pandas as pd

# Функция для получения соединения с базой данных
def get_db_connection():
    try:
        conn = sqlite3.connect('users_data.db')
        return conn
    except sqlite3.Error as e:
        print(f"Ошибка соединения с базой данных: {e}")
        return None

# Используем контекстный менеджер для работы с базой данных
with sqlite3.connect('users_data.db') as conn:
    c = conn.cursor()

    # Извлекаем данные из таблицы users
    c.execute('SELECT * FROM users')
    users = c.fetchall()

    # Получаем количество столбцов
    num_columns = len(users[0]) if users else 0
    print(f"Количество столбцов: {num_columns}")

# Если количество столбцов больше 9, можно вывести эти данные и адаптировать структуру
if num_columns == 9:
    columns = ['id', 'username', 'id_discord', 'level', 'experience', 'points', 'money', 'clan', 'registration_date']
elif num_columns > 9:
    columns = [f'column_{i}' for i in range(1, num_columns + 1)]  # Автоматическое создание заголовков
else:
    print("Неверное количество столбцов")
    columns = []  # В случае ошибки
    
# Создаем DataFrame с проверенными столбцами
df = pd.DataFrame(users, columns=columns)

# Записываем данные в Excel
df.to_excel('users_data.xlsx', index=False)

print("Данные успешно сохранены в файл users_data.xlsx")
