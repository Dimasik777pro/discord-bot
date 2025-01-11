import sqlite3
import pandas as pd
import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timezone  # Обновленный импорт

#######################################################################################################################################################

# Инициализация бота
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Необходим для работы с пользователями

# Инициализация бота
bot = commands.Bot(command_prefix="!", intents=intents)

############################################################################################################################################################


# ID создателя бота (можно заменить на свой)
OWNER_ID = 810897749817819136  # Замените на свой ID


# Проверка: только владелец бота может использовать эти команды
async def is_owner(interaction: discord.Interaction) -> bool:
    return interaction.user.id == OWNER_ID


###############################################################################################################################################################

# Словарь для хранения предупреждений
warnings = {}

#####################################################################################################################################################################



# Функция для подключения к базе данных SQLite
def get_db_connection():
    try:
        conn = sqlite3.connect('users_data.db')
        print("Подключение к базе данных установлено.")  # Логируем успешное подключение
        return conn
    except sqlite3.Error as e:
        print(f"Ошибка подключения к базе данных: {e}")  # Логируем ошибку подключения
        return None



# Функция для добавления новых столбцов, если они не существуют
def add_column_if_not_exists(cursor, table, column, column_definition):
    cursor.execute(f"PRAGMA table_info({table})")
    existing_columns = [column[1] for column in cursor.fetchall()]
    if column not in existing_columns:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_definition}")

# Функция для создания таблицы, если она не существует
def create_table():
    conn = get_db_connection()
    if conn:
        try:
            c = conn.cursor()
            # Создаем таблицу, если её нет
            c.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT UNIQUE,
                            id_discord TEXT,
                            level INTEGER DEFAULT 1,
                            experience INTEGER DEFAULT 0,
                            money INTEGER DEFAULT 0,
                            clan TEXT DEFAULT 'Не присоединился',
                            registration_date TEXT)''')
            
            # Добавляем столбец points, если его нет
            add_column_if_not_exists(c, 'users', 'points', 'INTEGER DEFAULT 0')

            conn.commit()
        except sqlite3.Error as e:
            print(f"Ошибка создания таблицы: {e}")
        finally:
            conn.close()

# Вызов функции для создания таблицы
create_table()



# Функция для добавления пользователя в базу данных
def add_user_to_db(username: str):
    print(f"Попытка добавить пользователя {username} в базу данных.")  # Логируем начало добавления
    conn = get_db_connection()
    if conn:
        try:
            # Создаем таблицу, если ее нет
            create_table()

            c = conn.cursor()
            
            # Используем INSERT OR IGNORE, чтобы избежать ошибки, если пользователь уже существует
            c.execute('INSERT OR IGNORE INTO users (username, points, level, experience) VALUES (?, ?, ?, ?)',
                      (username, 0, 0, 0))
            conn.commit()
            print(f"Пользователь {username} успешно добавлен в базу данных.")  # Логируем успешное добавление
        except sqlite3.Error as e:
            print(f"Ошибка при работе с базой данных: {e}")  # Логируем ошибки SQL
        finally:
            conn.close()
    else:
        print("Не удалось подключиться к базе данных.")  # Логируем, если соединение не установлено



#################################################################################################################################################



# Команда для экспорта данных из базы данных в Excel
@bot.command()
async def export(ctx):
    conn = get_db_connection()
    if conn:
        try:
            c = conn.cursor()
            c.execute('SELECT * FROM users')
            users = c.fetchall()

            # Создаем DataFrame из полученных данных
            columns = ['id', 'username', 'points', 'level', 'experience']
            df = pd.DataFrame(users, columns=columns)

            # Записываем данные в Excel
            df.to_excel('users_data.xlsx', index=False)
            await ctx.send("Данные успешно сохранены в файл users_data.xlsx")
        except Exception as e:
            await ctx.send(f"Ошибка экспорта данных: {e}")
        finally:
            conn.close()
    else:
        await ctx.send("Ошибка подключения к базе данных.")



#################################################################################################################################################



# Команда для получения информации о пользователе
@bot.command()
async def user_info(ctx, username: str):
    conn = get_db_connection()
    if conn:
        try:
            c = conn.cursor()
            c.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = c.fetchone()
            if user:
                await ctx.send(f"Информация о пользователе {username}:\n"
                               f"ID: {user[0]}\n"
                               f"Очки: {user[2]}\n"
                               f"Уровень: {user[3]}\n"
                               f"Опыт: {user[4]}")
            else:
                await ctx.send(f"Пользователь {username} не найден.")
        finally:
            conn.close()
    else:
        await ctx.send("Ошибка подключения к базе данных.")


# Команда для обновления уровня пользователя
@bot.command()
async def update_level(ctx, username: str, new_level: int):
    conn = get_db_connection()
    if conn:
        try:
            c = conn.cursor()
            c.execute('UPDATE users SET level = ? WHERE username = ?', (new_level, username))
            conn.commit()
            if c.rowcount > 0:
                await ctx.send(f"Уровень пользователя {username} обновлен на {new_level}.")
            else:
                await ctx.send(f"Пользователь {username} не найден.")
        finally:
            conn.close()
    else:
        await ctx.send("Ошибка подключения к базе данных.")



################################################################################################################################################



# Событие при запуске бота
@bot.event
async def on_ready():
    print(f'Бот подключен как {bot.user}')
    create_table()  # Создаем таблицу, если ее нет
    bot.start_time = datetime.now(timezone.utc)  # Добавляем время запуска
    try:
        synced = await bot.tree.sync()  # Синхронизируем команды
        print(f"Синхронизировано {len(synced)} команд.")
    except Exception as e:
        print(f"Ошибка синхронизации команд: {e}")



####################################################################################################################################################



# Команда /botinfo для получения информации о боте
@bot.tree.command(name="botinfo", description="Получите информацию о боте.")
async def botinfo(interaction: discord.Interaction):
    embed = discord.Embed(
        title=f"Информация о боте {bot.user.name}",
        color=discord.Color.blurple(),
        timestamp=datetime.now(timezone.utc)  # Используем timezone-aware объект
    )

    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else "")  # Устанавливаем аватарку бота
    embed.add_field(name="📌 Имя бота:", value=bot.user.name, inline=True)
    embed.add_field(name="🆔 ID бота:", value=bot.user.id, inline=True)
    embed.add_field(name="🖥 Серверов:", value=len(bot.guilds), inline=True)
    embed.add_field(name="👥 Пользователей:", value=sum(guild.member_count for guild in bot.guilds), inline=True)

    # Используем start_time, который установлен в on_ready()
    embed.add_field(name="⏱ Запущен:", value=f"<t:{int(bot.start_time.timestamp())}:R>", inline=True)
    embed.add_field(name="💻 Создан:", value=f"<t:{int(bot.user.created_at.timestamp())}:D>", inline=True)
    embed.add_field(name="⚙️ Префикс:", value=bot.command_prefix, inline=True)
    embed.set_footer(text=f"Запрошено: {interaction.user}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)

    await interaction.response.send_message(embed=embed)

####################################################################################################################



# Команда для проверки работы бота
@bot.tree.command(name="ping", description="Проверить работу бота")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Понг!")

####################################################################################################################



# Аватар
@bot.tree.command(name="avatar", description="Показать аватар пользователя или бота.")
async def avatar(interaction: discord.Interaction, user: discord.User = None):
    user = user or interaction.user

    embed = discord.Embed(
        title=f"Аватар пользователя {user.name}",
        color=discord.Color.blurple()
    )
    embed.set_image(url=user.avatar.url)  # Устанавливаем аватар пользователя или бота
    await interaction.response.send_message(embed=embed)



# Serverinfo
@bot.tree.command(name="serverinfo", description="Получить полную информацию о сервере.")
async def server_info(interaction: discord.Interaction):
    guild = interaction.guild

    embed = discord.Embed(
        title=f"Информация о сервере: {guild.name}",
        description="Подробная информация о текущем сервере.",
        color=discord.Color.blurple(),
        timestamp=discord.utils.utcnow()
    )

    embed.add_field(name="🌍 Название сервера", value=guild.name, inline=False)
    embed.add_field(name="📅 Дата создания", value=guild.created_at.strftime("%d.%m.%Y %H:%M:%S"), inline=True)

    if guild.owner:
        embed.add_field(name="👑 Владелец", value=guild.owner.mention, inline=True)
    else:
        embed.add_field(name="👑 Владелец", value="Sosisochka", inline=True)

    embed.add_field(name="🧑‍🤝‍🧑 Количество участников", value=str(guild.member_count), inline=True)

    embed.add_field(name="💬 Каналы", value=f"{len(guild.text_channels)} текстовых, {len(guild.voice_channels)} голосовых", inline=True)

    verification_level = {
        discord.VerificationLevel.low: "Низкий",
        discord.VerificationLevel.medium: "Средний",
        discord.VerificationLevel.high: "Высокий",
    }
    embed.add_field(name="🔒 Уровень безопасности", value=verification_level.get(guild.verification_level, "Неизвестно"), inline=True)

    embed.set_thumbnail(url=guild.icon.url if guild.icon else "https://i.imgur.com/fJ8HHkX.png")

    uptime = discord.utils.utcnow() - guild.created_at
    days, seconds = uptime.days, uptime.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    embed.add_field(name="⏳ Время с создания", value=f"{days} дней, {hours} часов, {minutes} минут", inline=True)

    await interaction.response.send_message(embed=embed)



# Команда для бана пользователя
@bot.tree.command(name="ban", description="Забанить пользователя")
async def ban(interaction: discord.Interaction, user: discord.User, reason: str = None):
    if interaction.user.guild_permissions.ban_members:
        await interaction.guild.ban(user, reason=reason)
        await interaction.response.send_message(f"Пользователь {user} забанен.")
    else:
        await interaction.response.send_message("У вас нет прав для бана пользователей.")



# Команда для разбана пользователя
@bot.tree.command(name="unban", description="Разбанить пользователя")
async def unban(interaction: discord.Interaction, user: discord.User):
    if interaction.user.guild_permissions.ban_members:
        await interaction.guild.unban(user)
        await interaction.response.send_message(f"Пользователь {user} разбанен.")
    else:
        await interaction.response.send_message("У вас нет прав для разбана пользователей.")



#KICK
@bot.tree.command(name="kick", description="Кикает пользователя с сервера")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "Нет причины"):
    """Кикает пользователя с сервера"""
    await member.kick(reason=reason)
    await interaction.response.send_message(f"{member.mention} был кикнут. Причина: {reason}")



###############################################################################################################################


# Функция для добавления пользователя в базу данных
def add_user_to_db(username: str):
    conn = get_db_connection()
    if conn:
        try:
            c = conn.cursor()
            c.execute('INSERT INTO users (username, points, level, experience) VALUES (?, ?, ?, ?)',
                      (username, 0, 0, 0))
            conn.commit()
        except sqlite3.IntegrityError:
            pass  # Пользователь уже существует
        finally:
            conn.close()




# Функция для подключения к базе данных SQLite
def get_db_connection():
    try:
        conn = sqlite3.connect('users_data.db')
        print("Подключение к базе данных установлено.")  # Логируем успешное подключение
        return conn
    except sqlite3.Error as e:
        print(f"Ошибка подключения к базе данных: {e}")  # Логируем ошибку подключения
        return None



###############################################################################################################################



# Функция для добавления пользователя в базу данных
def add_user_to_db(username: str):
    print(f"Попытка добавить пользователя {username} в базу данных.")  # Логируем начало добавления
    conn = get_db_connection()
    if conn:
        try:
            # Создаем таблицу, если ее нет
            create_table()

            c = conn.cursor()
            
            # Проверяем, существует ли пользователь в базе данных
            print(f"Проверка существования пользователя {username} в базе данных...")
            c.execute('SELECT id FROM users WHERE username = ?', (username,))
            user = c.fetchone()

            if user:
                print(f"Пользователь {username} уже существует в базе данных.")  # Логируем, если уже существует
            else:
                print(f"Пользователь {username} не найден в базе данных. Добавляем...")
                c.execute('INSERT INTO users (username, points, level, experience) VALUES (?, ?, ?, ?)',
                          (username, 0, 0, 0))
                conn.commit()
                print(f"Пользователь {username} успешно добавлен в базу данных.")  # Логируем успешное добавление
        except sqlite3.Error as e:
            print(f"Ошибка при работе с базой данных: {e}")  # Логируем ошибки SQL
        finally:
            conn.close()
    else:
        print("Не удалось подключиться к базе данных.")  # Логируем, если соединение не установлено



# Обработка команды /help
@bot.tree.command(name="help", description="Показать доступные команды и добавить пользователя в базу данных.")
async def help_command(interaction: discord.Interaction):
    # Добавляем пользователя в базу данных, если его нет
    add_user_to_db(interaction.user.name)

    # Создаем Embed для отображения команд
    embed = discord.Embed(
        title="Команды бота",
        description="Список доступных команд:",
        color=discord.Color.blurple()
    )
    embed.add_field(name="/botinfo", value="Получить информацию о боте", inline=False)
    embed.add_field(name="/ping", value="Проверить работу бота", inline=False)
    embed.add_field(name="/avatar", value="Показать аватар пользователя или бота", inline=False)
    embed.add_field(name="/serverinfo", value="Получить информацию о сервере", inline=False)

    await interaction.response.send_message(embed=embed)



###################################################################################################################################

  # Команды, доступные только создателю бота
@bot.tree.command(name="owner_command", description="Команда только для создателя бота")
async def owner_command(interaction: discord.Interaction):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("Эта команда доступна только создателю бота.")
        return
    
    await interaction.response.send_message("Команда выполнена! Это команда для создателя бота.")



# Пример другой команды только для создателя
@bot.tree.command(name="reset_db", description="Сбросить базу данных (только для создателя бота)")
async def reset_db(interaction: discord.Interaction):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("Эта команда доступна только создателю бота.")
        return

    conn = get_db_connection()
    if conn:
        try:
            c = conn.cursor()
            c.execute("DROP TABLE IF EXISTS users")  # Удаляем таблицу пользователей
            conn.commit()
            await interaction.response.send_message("База данных сброшена.")
        except sqlite3.Error as e:
            await interaction.response.send_message(f"Ошибка при сбросе базы данных: {e}")
        finally:
            conn.close()



# Команда для получения списка всех пользователей из базы данных
@bot.tree.command(name="list_users", description="Получить список всех пользователей (только для создателя бота)")
async def list_users(interaction: discord.Interaction):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("Эта команда доступна только создателю бота.")
        return

    conn = get_db_connection()
    if conn:
        try:
            c = conn.cursor()
            c.execute("SELECT username, points, level, experience FROM users")
            users = c.fetchall()

            if users:
                user_list = "\n".join([f"Пользователь: {user[0]}, Очки: {user[1]}, Уровень: {user[2]}, Опыт: {user[3]}" for user in users])
                await interaction.response.send_message(f"Список пользователей:\n{user_list}")
            else:
                await interaction.response.send_message("Нет пользователей в базе данных.")
        except sqlite3.Error as e:
            await interaction.response.send_message(f"Ошибка при получении списка пользователей: {e}")
        finally:
            conn.close()



# Команда для удаления пользователя из базы данных
@bot.tree.command(name="delete_user", description="Удалить пользователя из базы данных (только для создателя бота)")
async def delete_user(interaction: discord.Interaction, username: str):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("Эта команда доступна только создателю бота.")
        return

    conn = get_db_connection()
    if conn:
        try:
            c = conn.cursor()
            c.execute('DELETE FROM users WHERE username = ?', (username,))
            conn.commit()
            if c.rowcount > 0:
                await interaction.response.send_message(f"Пользователь {username} удален из базы данных.")
            else:
                await interaction.response.send_message(f"Пользователь {username} не найден.")
        except sqlite3.Error as e:
            await interaction.response.send_message(f"Ошибка при удалении пользователя: {e}")
        finally:
            conn.close()  





# Команда для выключения бота
@bot.tree.command(name="shutdown", description="Выключает бота (только для создателя)")
async def shutdown(interaction: discord.Interaction):
    if not await is_owner(interaction):
        await interaction.response.send_message("У вас нет прав для использования этой команды.", ephemeral=True)
        return
    await interaction.response.send_message("Бот выключается...", ephemeral=True)
    await bot.close()



@bot.tree.command(name="list_servers", description="Показывает список серверов, где находится бот (только для создателя)")
async def list_servers(interaction: discord.Interaction):
    if not await is_owner(interaction):
        await interaction.response.send_message("У вас нет прав для использования этой команды.", ephemeral=True)
        return

    server_info = []
    for guild in bot.guilds:
        try:
            # Получаем первое доступное приглашение
            invites = await guild.invites()
            if invites:
                invite_url = invites[0].url
            else:
                # Создаем новое приглашение, если доступно
                for channel in guild.text_channels:
                    if channel.permissions_for(guild.me).create_instant_invite:
                        invite_url = await channel.create_invite(max_age=0, max_uses=0, unique=False)
                        invite_url = invite_url.url
                        break
                else:
                    invite_url = "Нет доступных приглашений"
        except discord.Forbidden:
            invite_url = "Нет прав на просмотр/создание приглашений"

        server_info.append(f"**{guild.name}** — [Ссылка на сервер]({invite_url})")

    if not server_info:
        await interaction.response.send_message("Бот не состоит ни на одном сервере.", ephemeral=True)
    else:
        response = "\n".join(server_info)
        await interaction.response.send_message(f"Список серверов, где находится бот:\n{response}", ephemeral=True)



# Команда для отправки системного сообщения (например, обновлений)
@bot.tree.command(name="broadcast", description="Отправляет сообщение всем серверам (только для создателя)")
async def broadcast(interaction: discord.Interaction, message: str):
    if not await is_owner(interaction):
        await interaction.response.send_message("У вас нет прав для использования этой команды.", ephemeral=True)
        return
    for guild in bot.guilds:
        for channel in guild.text_channels:
            try:
                await channel.send(message)
                break
            except discord.Forbidden:
                continue
    await interaction.response.send_message("Сообщение отправлено всем доступным серверам.", ephemeral=True)



# Команда для проверки количества участников на всех серверах
@bot.tree.command(name="member_count", description="Показывает общее количество участников (только для создателя)")
async def member_count(interaction: discord.Interaction):
    if not await is_owner(interaction):
        await interaction.response.send_message("У вас нет прав для использования этой команды.", ephemeral=True)
        return
    total_members =     sum(guild.member_count for guild in bot.guilds)
    await interaction.response.send_message(f"Общее количество участников на всех серверах: {total_members}", ephemeral=True)







# Запуск бота
bot.run('MTI1MzY4MzgxMTA1NzkzMDMyMg.GRd21K._LnfC_6IpXrcFmf2TkG4m99F9r55dBN99DnqDM')
