from telegram import Update, InputMediaPhoto
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, ConversationHandler, filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
import mysql.connector
import os

class DatabaseManager:
    def create_table():
        conn = mysql.connector.connect(
            host="localhost",
            user="root",       # Логин MySQL
            password="",       # Пароль MySQL
            database="characters"  # Название базы данных
        )
        cursor = conn.cursor()
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS characters (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id BIGINT NOT NULL,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                health INT,
                abilities TEXT,
                skills TEXT,
                avatar VARCHAR(255),
                damage INT DEFAULT 0
            )
        ''')
        conn.commit()
        conn.close()
        
    def save_character_to_db(character, user_id):
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="characters"
        )
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO characters (user_id, name, description, health, abilities, skills, avatar, damage)
                        VALUES (%s, %s, %s, %s, %s, %s, %s,%s)''',
                    (user_id, character['name'], character['description'], character['health'],
                        character['abilities'], character['skills'], character['avatar'], character['damage']))
        conn.commit()
    
        # Get the ID of the newly inserted character
        character_id = cursor.lastrowid
        conn.close()
        return character_id
    #Здесь связоные с командами
    #/delete - 
    async def delete_character(update: Update, context: CallbackContext):
        if len(context.args) != 1:
            await update.message.reply_text("Пожалуйста, укажите ID персонажа с помощью /delete <id>.")
            return
    
        try:
            character_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text("ID персонажа должно быть числом.")
            return
    
        user_id = update.message.from_user.id  # ID пользователя
    
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="characters"
        )
        cursor = conn.cursor()
    
        try:
            # Проверяем, существует ли персонаж с таким ID, принадлежащий этому пользователю
            cursor.execute("SELECT id FROM characters WHERE id=%s AND user_id=%s", (character_id, user_id))
            character = cursor.fetchone()
    
            if character is None:
                await update.message.reply_text(f"Персонаж с ID {character_id} не существует или вам не принадлежит.")
                return
    
            # Если персонаж найден, удаляем его
            cursor.execute("DELETE FROM characters WHERE id=%s AND user_id=%s", (character_id, user_id))
            conn.commit()
    
            await update.message.reply_text(f"Персонаж с ID {character_id} был успешно удален.")
        finally:
            cursor.close()
            conn.close()
    #/list
    async def list_characters(update: Update, context: CallbackContext):
        user_id = update.message.from_user.id  # Get the user ID of the person making the request
    
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="characters"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM characters WHERE user_id=%s", (user_id,))
        characters = cursor.fetchall()
        conn.close()
    
        if characters:
            response = "Список ваших персонажей:\n"
            for character in characters:
                response += f"🆔 {character[0]} - {character[1]}\n"
            await update.message.reply_text(response)
        else:
            await update.message.reply_text("Персонажи не найдены. Создайте персонажа с помощью /create.")
    #/show -
    async def show_character(update: Update, context: CallbackContext):
        if len(context.args) != 1:
            await update.message.reply_text("Пожалуйста, укажите ID персонажа с помощью /show <id>.")
            return
    
        try:
            character_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text("ID персонажа должно быть числом.")
            return
    
        user_id = update.message.from_user.id  # Get the user ID of the person making the request
    
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="characters"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM characters WHERE id=%s AND user_id=%s", (character_id, user_id))
        character = cursor.fetchone()
        conn.close()
    
        if character:
            avatar_path = character[7]  # Assuming avatar is stored in the 8th column
            user_folder = "avatars/"
            No_avatar_path = os.path.join(user_folder, "NoAvatarce.jpg")
    
            if os.path.exists(avatar_path):
                with open(avatar_path, 'rb') as avatar_file:
                    message = (
                        f"<b>Персонаж:</b> {character[2]}\n\n"
                        f"<b>🆔ID:</b> {character[0]}\n"
                        f"<b>🏷️Имя:</b> {character[2]}\n"
                        f"<b>📝Описание:</b> {character[3]}\n"
                        f"<b>❤️Здоровье:</b> {character[4]}\n"
                        f"<b>🔪Урон:</b> {character[8]}\n"
                        f"<b>🧠Способности:</b> {character[5]}\n"
                        f"<b>⚒️Навыки:</b> {character[6]}\n"
                    )
                    await update.message.reply_photo(
                        photo=avatar_file,
                        caption=message,
                        parse_mode=ParseMode.HTML
                    )
            else:
                with open(No_avatar_path, 'rb') as No_avatar_path:
                    message = (
                        f"<b>Персонаж:</b> {character[2]}\n\n"
                        f"<b>🆔ID:</b> {character[0]}\n"
                        f"<b>🏷️Имя:</b> {character[2]}\n"
                        f"<b>📝Описание:</b> {character[3]}\n"
                        f"<b>❤️Здоровье:</b> {character[4]}\n"
                        f"<b>🔪Урон:</b> {character[8]}\n"
                        f"<b>🧠Способности:</b> {character[5]}\n"
                        f"<b>⚒️Навыки:</b> {character[6]}\n"
                    )
                    await update.message.reply_photo(
                        photo=No_avatar_path,
                        caption=message,
                        parse_mode=ParseMode.HTML
                    )
        else:
            await update.message.reply_text(f"Персонаж с ID {character_id} не найден или не принадлежит вам.")

