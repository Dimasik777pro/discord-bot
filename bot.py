import pandas as pd
import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timezone
from discord.ui import View, Select
import random


# Инициализация бота
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Необходим для работы с пользователями

bot = commands.Bot(command_prefix="!", intents=intents)

#######################################################################Статусы бота###########################################################################################

@bot.event
async def on_ready():
    print(f'Бот подключился как {bot.user}')
    # Устанавливаем статус, когда бот запускается
    await update_activity()

async def update_activity():
    # Бот будет показывать активность на основе типичного действия
    activity = discord.Game(name="Играю в шахматы!")
    await bot.change_presence(activity=activity)

@bot.command()
async def play_game(ctx, *, game_name: str):
    # Изменить активность на "играет в <игра>"
    activity = discord.Game(name=f"Играю в {game_name}")
    await bot.change_presence(activity=activity)
    await ctx.send(f"Теперь я играю в {game_name}!")

@bot.command()
async def listen_music(ctx, *, song_name: str):
    # Изменить активность на "слушает <песня>"
    activity = discord.Activity(type=discord.ActivityType.listening, name=song_name)
    await bot.change_presence(activity=activity)
    await ctx.send(f"Теперь я слушаю {song_name}!")

async def video_bot(ctx, *, video_name: str):
    # Изменить активность на "смотрит видео"
    activity = discord.Activity(type=discord.ActivityType.watching, name=video_name)
    await bot.change_presence(activity=activity)
    await ctx.send(f"Теперь я смотрю {video_name}!")

##################################################################################База данных##################################################################################

# Словарь для хранения настроек сервера
server_settings = {}


# ID создателя бота (можно заменить на свой ID)
OWNER_ID = 810897749817819136 # Замените на свой ID

def is_owner():
    async def predicate(ctx):
        if ctx.author.id != OWNER_ID:
            print(f"Отказано в доступе: {ctx.author} (ID: {ctx.author.id}) попытался использовать команду.")
            return False  # Вернет False, если пользователь не является владельцем
        return True  # Вернет True, если пользователь — владелец
    return commands.check(predicate)





# Путь к Excel файлу для хранения данных
EXCEL_FILE = 'users_data.xlsx'

# Функция для проверки существования файлов и создания их, если они не существуют
def create_excel_file(file_path, columns):
    try:
        pd.read_excel(file_path)
    except FileNotFoundError:
        df = pd.DataFrame(columns=columns)
        df.to_excel(file_path, index=False)
        print(f"Создан новый файл {file_path}.")

# Инициализация файла
create_excel_file(EXCEL_FILE, ["id", "username", "id_discord", "level", "experience", "money", "registration_date", "points"])

# Проверка прав администратора
def is_admin(interaction: discord.Interaction) -> bool:
    return interaction.user.guild_permissions.administrator

# Событие для синхронизации команд при запуске бота
@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Синхронизировано {len(synced)} команд.")
    except Exception as e:
        print(f"Ошибка при синхронизации команд: {e}")


#########################################################################################Команды##################################################################################################

#ping
@bot.tree.command(name="ping", description="Узнать время отклика бота.")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"Понг! Задержка: {latency} мс.")



# Команда для получения аватара с использованием слеш-команды
@bot.tree.command(name="avatar", description="Получить аватар пользователя")
async def avatar(interaction: discord.Interaction, user: discord.Member = None):
    # Если пользователь не указан, то берем аватар отправителя
    user = user or interaction.user
    await interaction.response.send_message(user.avatar.url)


# Команда для получения информации о пользователе
@bot.tree.command(name="user", description="Информация о пользователе")
async def user_info(interaction: discord.Interaction, user: discord.Member = None):
    # Если пользователь не указан, то берем информацию о отправителе
    user = user or interaction.user

    # Формируем сообщение с информацией о пользователе
    embed = discord.Embed(title=f"Информация о пользователе {user}", color=discord.Color.blue())
    embed.add_field(name="Имя", value=user.name, inline=True)
    embed.add_field(name="Тег", value=user.discriminator, inline=True)
    embed.add_field(name="ID", value=user.id, inline=False)
    embed.add_field(name="Дата вступления", value=user.joined_at.strftime("%d/%m/%Y %H:%M:%S"), inline=True)
    embed.add_field(name="Дата создания аккаунта", value=user.created_at.strftime("%d/%m/%Y %H:%M:%S"), inline=True)
    embed.set_thumbnail(url=user.avatar.url)

    # Отправляем информацию пользователю
    await interaction.response.send_message(embed=embed)




#serverinfo
@bot.tree.command(name="serverinfo", description="Подробная информация о сервере")
async def server_info(interaction: discord.Interaction):
    guild = interaction.guild  # Получаем текущий сервер
    owner = guild.owner  # Владелец сервера
    created_at = guild.created_at.strftime("%d %B %Y г. %H:%M")  # Дата создания сервера
    age_days = (datetime.now(timezone.utc) - guild.created_at).days  # Возраст сервера в днях
    age_years = age_days // 365  # Полные годы
    age_months = (age_days % 365) // 30  # Месяцы (с остатком от дней)

    total_channels = len(guild.channels)  # Всего каналов
    text_channels = len([c for c in guild.channels if isinstance(c, discord.TextChannel)])
    voice_channels = len([c for c in guild.channels if isinstance(c, discord.VoiceChannel)])
    stage_channels = len([c for c in guild.channels if isinstance(c, discord.StageChannel)])
    announce_channels = len([c for c in guild.channels if isinstance(c, discord.TextChannel) and c.is_news()])
    categories = len(guild.categories)  # Категории
    total_members = guild.member_count  # Всего пользователей
    bots = len([m for m in guild.members if m.bot])  # Боты
    users = total_members - bots  # Участники

    # Уровень буста
    boost_level = guild.premium_tier
    boosts = guild.premium_subscription_count

    # Дата последнего буста (эмуляция, так как Discord API этого не предоставляет)
    boosters = [m for m in guild.members if m.premium_since]
    booster_list = ""
    for booster in boosters:
        booster_list += f"{booster.mention} — {booster.premium_since.strftime('%d %B %Y')}\n"

    # Формируем Embed-сообщение
    embed = discord.Embed(
        title=f"Информация о сервере {guild.name}",
        color=discord.Color.green()
    )
    embed.add_field(name="Основное", value=( 
        f"🧑‍💼 Владелец: {owner.mention} ({owner.id})\n"
        f"✅ Уровень проверки: {guild.verification_level.name.capitalize()}\n"
        f"🖼️ Создан: {created_at} ({age_years} лет, {age_months} месяцев назад)\n"
        f"📡 Всего {total_channels} каналов\n"
        f"💬 Текстовые каналы: {text_channels}\n"
        f"🎤 Голосовые каналы: {voice_channels}\n"
        f"🎙️ Трибуны: {stage_channels}\n"
        f"📢 Новостные каналы: {announce_channels}\n"
        f"📂 Категории: {categories}\n"
    ), inline=False)

    embed.add_field(name="Пользователи", value=(
        f"👥 Всего {total_members} пользователей\n"
        f"🤖 Ботов: {bots}\n"
        f"🙋‍♂️ Участников: {users}\n"
    ), inline=False)

    embed.add_field(name="Бусты", value=(
        f"🚀 Уровень: {boost_level} (бустов — {boosts})\n"
        f"{booster_list if booster_list else 'Нет информации о бустерах.'}"
    ), inline=False)

    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)  # Устанавливаем иконку сервера
    await interaction.response.send_message(embed=embed)


#info bot
@bot.tree.command(name="info", description="Информация о боте")
async def info_command(interaction: discord.Interaction):
    bot_name = bot.user.name  # Имя бота
    bot_id = bot.user.id  # ID бота
    bot_nick = bot.user.name  # Используем имя бота как ник, если он не установлен
    bot_uptime = interaction.created_at  # Время начала взаимодействия с ботом
    bot_creation_date = bot.user.created_at.strftime("%Y-%m-%d %H:%M:%S")  # Дата создания аккаунта бота
    creator = "mr.sosisochka"  # Имя создателя бота
    team_size = 5  # Количество человек, работающих над проектом
    bot_avatar = bot.user.avatar.url  # Ссылка на аватар бота

    # Форматируем информацию о боте
    embed = discord.Embed(
        title="Информация о боте",
        description=f"Бот {bot_name} ({bot_id})",
        color=discord.Color.blue()
    )
    embed.add_field(name="Ник бота", value=bot_nick, inline=False)
    embed.add_field(name="Дата создания бота", value=bot_creation_date, inline=False)
    embed.add_field(name="Дата запуска", value=bot_uptime.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
    embed.add_field(name="Создатель", value=creator, inline=False)
    embed.add_field(name="Человек в команде", value=team_size, inline=False)
    embed.set_footer(text="Бот создан на discord.py")
    embed.set_thumbnail(url=bot_avatar)  # Устанавливаем аватар в качестве миниатюры

    # Отправляем embed-сообщение с информацией о боте
    await interaction.response.send_message(embed=embed)

#serverstats
@bot.tree.command(name="serverstats", description="Показать статистику сервера")
async def serverstats(interaction: discord.Interaction):
    # Получение статистики сервера
    server = interaction.guild
    message_count = 0  # Пока нет статистики сообщений в этом примере
    member_count = server.member_count  # Общее количество пользователей
    bot_count = sum(1 for member in server.members if member.bot)  # Количество ботов
    text_channels = len([channel for channel in server.channels if isinstance(channel, discord.TextChannel)])  # Количество текстовых каналов
    voice_channels = len([channel for channel in server.channels if isinstance(channel, discord.VoiceChannel)])  # Количество голосовых каналов

    # Создание Embed с информацией о сервере
    embed = discord.Embed(title=f"Статистика сервера {server.name}",
                          description="**Общая информация о сервере:**")
    embed.add_field(name="Сообщений на сервере:", value=str(message_count), inline=False)
    embed.add_field(name="Количество пользователей:", value=str(member_count), inline=False)
    embed.add_field(name="Количество ботов:", value=str(bot_count), inline=False)
    embed.add_field(name="Количество текстовых каналов:", value=str(text_channels), inline=False)
    embed.add_field(name="Количество голосовых каналов:", value=str(voice_channels), inline=False)

    # Отправка Embed сообщения
    await interaction.response.send_message(embed=embed)

        




#newrole 
APPLICATION_CHANNEL = "role-requests"  # Название канала для заявок

@bot.tree.command(name="newrole", description="Подать заявку на новую роль.")
async def newrole(interaction: discord.Interaction, role_name: str):
    application_channel = discord.utils.get(interaction.guild.text_channels, name=APPLICATION_CHANNEL)
    if not application_channel:
        await interaction.response.send_message(
            f"Канал `{APPLICATION_CHANNEL}` не найден. Попросите администратора создать его.", ephemeral=True
        )
        return

    # Уведомляем пользователя
    await interaction.response.send_message(f"Ваша заявка на роль `{role_name}` отправлена на рассмотрение!", ephemeral=True)

    # Создаём сообщение с заявкой в канал модераторов
    embed = discord.Embed(
        title="Новая заявка на роль",
        description=f"Пользователь {interaction.user.mention} подал заявку на роль `{role_name}`.",
        color=discord.Color.blue(),
    )
    embed.set_footer(text=f"ID пользователя: {interaction.user.id}")

    msg = await application_channel.send(embed=embed)
    await msg.add_reaction("✅")  # Реакция для одобрения
    await msg.add_reaction("❌")  # Реакция для отклонения

@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    if payload.member.bot:
        return

    guild = bot.get_guild(payload.guild_id)
    channel = guild.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)

    if message.author != bot.user or not message.embeds:
        return

    embed = message.embeds[0]
    if payload.emoji.name == "✅":
        user_id = int(embed.footer.text.split(": ")[-1])
        member = guild.get_member(user_id)
        role_name = embed.description.split("`")[-2]

        role = discord.utils.get(guild.roles, name=role_name)
        if not role:
            role = await guild.create_role(name=role_name)

        await member.add_roles(role)
        await channel.send(f"Роль `{role_name}` была успешно добавлена пользователю {member.mention}.")
        await message.delete()

    elif payload.emoji.name == "❌":
        user_id = int(embed.footer.text.split(": ")[-1])
        member = guild.get_member(user_id)
        role_name = embed.description.split("`")[-2]

        await channel.send(f"Заявка на роль `{role_name}` от пользователя {member.mention} была отклонена.")
        await message.delete()




#############################################################Команды админов################################################################

#addrole
@bot.tree.command(name="addrole", description="Добавляет роль пользователю.")
async def add_role(interaction: discord.Interaction, user: discord.Member, role: discord.Role):
    if interaction.user.guild_permissions.administrator:
        await user.add_roles(role)
        await interaction.response.send_message(f"Роль {role.name} была добавлена пользователю {user.mention}.")
    else:
        await interaction.response.send_message("У вас нет прав для добавления роли.")


#removerole
@bot.tree.command(name="removerole", description="Удаляет роль у пользователя.")
async def remove_role(interaction: discord.Interaction, user: discord.Member, role: discord.Role):
    if interaction.user.guild_permissions.administrator:
        await user.remove_roles(role)
        await interaction.response.send_message(f"Роль {role.name} была удалена у пользователя {user.mention}.")
    else:
        await interaction.response.send_message("У вас нет прав для удаления роли.")



#say
@bot.tree.command(name="say", description="Отправить сообщение от имени бота.")
@app_commands.default_permissions(administrator=True)
async def say(interaction: discord.Interaction, message: str):
    """Команда /say для отправки сообщения от имени бота."""
    try:
        # Удаление исходного сообщения пользователя
        await interaction.response.defer(ephemeral=True)  # Ответ пользователю
        await interaction.delete_original_response()

        # Отправка сообщения от имени бота
        await interaction.channel.send(message)
    except Exception as e:
        await interaction.followup.send(f"Произошла ошибка: {e}", ephemeral=True)



# Команда для очистки сообщений (доступна только администраторам)
@bot.tree.command(name="clear", description="Удалить определенное количество сообщений")
@commands.has_permissions(administrator=True)  # Проверка, что пользователь администратор
async def clear_messages(interaction: discord.Interaction, amount: int):
    # Проверяем, что количество сообщений от 1 до 100
    if amount < 1 or amount > 100:
        await interaction.response.send_message("Пожалуйста, укажите число от 1 до 100.", ephemeral=True)
        return

    # Удаляем сообщения
    deleted = await interaction.channel.purge(limit=amount)
    
    # Отправляем сообщение, сколько сообщений было удалено
    await interaction.response.send_message(f"Удалено {len(deleted)} сообщений.", ephemeral=True)



################################################################################Команды владельца бота########################################################################################


#broadcast
@bot.command(name="broadcast", description="Отправляет сообщение на все сервера (только владелец)")
@is_owner()
async def broadcast(ctx, message: str):
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                try:
                    await channel.send(f"📢 Объявление от владельца: {message}")
                    print(f"Сообщение отправлено в {guild.name} на канал {channel.name}")
                    break
                except Exception as e:
                    print(f"Ошибка при отправке в {guild.name}: {e}")
                    continue
    await ctx.send("✅ Сообщение отправлено на все сервера!")


#dm
@bot.command(name="dm", description="Отправляет личное сообщение пользователю (только владелец)")
@is_owner()
async def dm(ctx, member: discord.Member, message: str):
    try:
        await member.send(message)
        await ctx.send(f"✅ Сообщение отправлено {member.mention}!")
    except Exception as e:
        print(f"Ошибка при отправке сообщения {member}: {e}")
        await ctx.send("⚠️ Не удалось отправить сообщение.")

#guild_list
@bot.command(name="guild_list", description="Выводит список всех серверов, на которых находится бот (только владелец)")
@is_owner()
async def guild_list(ctx):
    guild_names = "\n".join([f"[{guild.name}](https://discord.com/channels/{guild.id})" for guild in bot.guilds])
    await ctx.send(f"📜 Бот находится на следующих серверах:\n{guild_names}")


#commands_list
@bot.command(name="commands_list", description="Показывает список всех команд бота (только владелец)")
@is_owner()
async def commands_list(ctx):
    commands = "\n".join([command.name for command in bot.commands])
    await ctx.send(f"📜 Доступные команды:\n{commands}")














#######################################################################help#################################################################

# Команда для отображения списка команд бота
@bot.tree.command(name="help", description="Показать список доступных команд.")
async def help_command(interaction: discord.Interaction):
    help_text = """
    **Список доступных команд:**

    /ping - Узнать время отклика бота.
    /avatar [user] - Получить аватар пользователя.
    /user [user] - Получить информацию о пользователе.
    /clear [amount] - Удалить определенное количество сообщений (только для администраторов).
    /serverinfo - Информация о сервере.
    /info - Информация о боте.
    /serverstats - Статистика сервера.
    /say [message] - Отправить сообщение от имени бота (только для администраторов).
    /newrole [role_name] - Подать заявку на новую роль.
    """
    await interaction.response.send_message(help_text, ephemeral=True)

##############################################################################################################



# Запуск бота
bot.run('MTI1MzY4MzgxMTA1NzkzMDMyMg.GRd21K._LnfC_6IpXrcFmf2TkG4m99F9r55dBN99DnqDM')
