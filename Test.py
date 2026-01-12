from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, TypeHandler, CommandHandler
import logging
import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import html

# Настройка логирования

logging.basicConfig(
format=’%(asctime)s - %(name)s - %(levelname)s - %(message)s’,
level=logging.INFO
)
logger = logging.getLogger(**name**)

# Конфигурация

BOT_TOKEN = “8557947353:AAFf4WeRSnZw3aJz1kllmy3euBLPcluZLus”
DATA_DIR = Path(“user_data”)
MEDIA_DIR = Path(“saved_once_media”)
DATA_DIR.mkdir(exist_ok=True)
MEDIA_DIR.mkdir(exist_ok=True)

# Глобальное хранилище: {user_id: {…данные…}}

USER_DATA: Dict[int, Dict[str, Any]] = {}

# Маппинг business_connection_id -> user_id

BUSINESS_CONNECTIONS: Dict[str, int] = {}

def get_user_file(user_id: int) -> Path:
“”“Возвращает путь к файлу пользователя”””
return DATA_DIR / f”user_{user_id}.json”

def load_user_data(user_id: int):
“”“Загружает данные пользователя”””
if user_id in USER_DATA:
return USER_DATA[user_id]

```
user_file = get_user_file(user_id)
if user_file.exists():
    try:
        with open(user_file, 'r', encoding='utf-8') as f:
            USER_DATA[user_id] = json.load(f)
            logger.info(f"✅ Загружены данные пользователя {user_id}")
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки данных {user_id}: {e}")
        USER_DATA[user_id] = {
            "messages": {}, 
            "stats": {"received": 0, "sent": 0, "view_once": 0},
            "business_connections": []
        }
else:
    USER_DATA[user_id] = {
        "messages": {}, 
        "stats": {"received": 0, "sent": 0, "view_once": 0},
        "business_connections": []
    }

return USER_DATA[user_id]
```

def save_user_data(user_id: int):
“”“Сохраняет данные пользователя”””
if user_id not in USER_DATA:
return

```
try:
    user_file = get_user_file(user_id)
    with open(user_file, 'w', encoding='utf-8') as f:
        json.dump(USER_DATA[user_id], f, ensure_ascii=False, indent=2, default=str)
    logger.info(f"💾 Сохранены данные пользователя {user_id}")
except Exception as e:
    logger.error(f"❌ Ошибка сохранения данных {user_id}: {e}")
```

def escape_markdown(text: str) -> str:
“”“Экранирует специальные символы для Markdown”””
if not text:
return “”
# Экранируем только самые критичные символы
escape_chars = [’_’, ‘*’, ‘[’, ‘]’, ‘(’, ‘)’, ‘~’, ‘`’, ‘>’, ‘#’, ‘+’, ‘-’, ‘=’, ‘|’, ‘{’, ‘}’, ‘.’, ‘!’]
for char in escape_chars:
text = text.replace(char, f’\{char}’)
return text

def format_datetime(dt) -> str:
“”“Форматирует дату в DD.MM.YYYY HH:MM”””
if isinstance(dt, str):
try:
dt = datetime.fromisoformat(dt)
except:
return “N/A”
if isinstance(dt, datetime):
return dt.strftime(”%d.%m.%Y %H:%M”)
return “N/A”

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
“”“Команда /start”””
user = update.effective_user
user_data = load_user_data(user.id)

```
await update.message.reply_text(
    f"👋 Привет, {user.first_name}\\!\n\n"
    f"🤖 Я логирую все твои сообщения в бизнес\\-чатах\\.\n\n"
    f"📋 *Что я умею:*\n"
    f"• Сохраняю все сообщения\n"
    f"• Отслеживаю удаления\n"
    f"• Отслеживаю редактирования\n"
    f"• Перехватываю View Once медиа\n\n"
    f"Используй /help для справки",
    parse_mode='MarkdownV2'
)
```

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
“”“Команда /help”””
help_text = “””
🤖 *СПРАВКА*

📌 *Команды:*
/start \- Приветствие
/stats \- Твоя статистика
/help \- Эта справка

📝 *Что логируется:*
✓ Все входящие и исходящие сообщения
✓ Удаления \(с указанием, кто удалил\)
✓ Редактирования \(было/стало\)
✓ View Once фото и видео

💡 *Важно:* Твои данные приватны и не пересекаются с другими пользователями\!
“””
await update.message.reply_text(help_text, parse_mode=‘MarkdownV2’)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
“”“Команда /stats - персональная статистика”””
user = update.effective_user
user_data = load_user_data(user.id)
stats = user_data.get(“stats”, {“received”: 0, “sent”: 0, “view_once”: 0})

```
stats_text = "📊 *Ваша статистика \\(ЛС\\)*\n\n"
stats_text += f"📥 Получено сообщений: `{stats.get('received', 0)}`\n"
stats_text += f"📤 Отправлено сообщений: `{stats.get('sent', 0)}`\n"
stats_text += f"🔥 View Once медиа: `{stats.get('view_once', 0)}`"

await update.message.reply_text(stats_text, parse_mode='MarkdownV2')
```

async def save_view_once(msg, context: ContextTypes.DEFAULT_TYPE, user_id: int, media_type: str):
“”“Сохраняет View Once медиа БЕЗ ошибок”””
try:
file_id = None
caption = getattr(msg, “caption”, None) or “”
timestamp = datetime.now().strftime(”%Y%m%d_%H%M%S”)

```
    if media_type == "photo" and msg.photo:
        file_id = msg.photo[-1].file_id
        extension = ".jpg"
        emoji = "🖼"
    elif media_type == "video" and msg.video:
        file_id = msg.video.file_id
        extension = ".mp4"
        emoji = "🎥"
    elif media_type == "video_note" and msg.video_note:
        file_id = msg.video_note.file_id
        extension = ".mp4"
        emoji = "⭕️"
    else:
        return

    if not file_id:
        return

    filename = MEDIA_DIR / f"{timestamp}_{msg.message_id}_{media_type}{extension}"

    # Сохраняем файл
    file = await context.bot.get_file(file_id)
    await file.download_to_drive(str(filename))
    file_size = filename.stat().st_size / 1024
    
    # Обновляем статистику
    user_data = load_user_data(user_id)
    user_data["stats"]["view_once"] = user_data["stats"].get("view_once", 0) + 1
    save_user_data(user_id)
    
    # Формируем безопасное сообщение (БЕЗ MARKDOWN для избежания ошибок парсинга)
    sender_info = ""
    if msg.from_user:
        username = f"@{msg.from_user.username}" if msg.from_user.username else msg.from_user.full_name
        sender_info = f"\n{username} | ID: {msg.from_user.id}"
    
    if msg.chat:
        chat_name = msg.chat.title or msg.chat.first_name or "Личный чат"
        sender_info += f"\nЧат: {chat_name}"
    
    sender_info += f"\nВремя: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    sender_info += f"\nРазмер: {file_size:.1f} KB"

    # ВАЖНО: отправляем БЕЗ parse_mode для избежания ошибок
    full_caption = f"🔥 VIEW ONCE {emoji}{sender_info}"
    if caption:
        full_caption += f"\n\nПодпись: {caption}"

    # Отправляем медиа с обычным текстом (без Markdown)
    with open(filename, 'rb') as f:
        if media_type == "photo":
            await context.bot.send_photo(user_id, photo=f, caption=full_caption)
        elif media_type == "video":
            await context.bot.send_video(user_id, video=f, caption=full_caption)
        elif media_type == "video_note":
            await context.bot.send_video_note(user_id, video_note=f)
            await context.bot.send_message(user_id, full_caption)
    
    logger.info(f"✅ View Once сохранено для пользователя {user_id}")
    
except Exception as e:
    # Ошибки НЕ показываем пользователю, только логируем
    logger.error(f"❌ View Once ошибка (НЕ отправлено пользователю): {e}")
```

async def handle_all_updates(update: Update, context: ContextTypes.DEFAULT_TYPE):
“”“Главный обработчик всех обновлений”””

```
# ОБРАБОТКА БИЗНЕС-ПОДКЛЮЧЕНИЯ
if update.business_connection:
    conn = update.business_connection
    user_id = conn.user.id
    connection_id = conn.id
    
    # Сохраняем связь connection_id -> user_id
    BUSINESS_CONNECTIONS[connection_id] = user_id
    
    # Добавляем в данные пользователя
    user_data = load_user_data(user_id)
    if connection_id not in user_data.get("business_connections", []):
        user_data["business_connections"] = user_data.get("business_connections", [])
        user_data["business_connections"].append(connection_id)
        save_user_data(user_id)
    
    logger.info(f"🔗 Бизнес-подключение: user={user_id}, connection={connection_id}")
    
    # Уведомляем пользователя
    try:
        await context.bot.send_message(
            user_id,
            f"🔗 *Бизнес\\-аккаунт подключен\\!*\n\n"
            f"✅ Начинаю логировать все сообщения\n"
            f"📊 Используй /stats для статистики",
            parse_mode='MarkdownV2'
        )
    except:
        pass
    
    return

# Определяем владельца по business_connection_id
def get_owner_from_message(msg) -> int:
    """Определяет владельца по сообщению"""
    if hasattr(msg, 'business_connection_id') and msg.business_connection_id:
        return BUSINESS_CONNECTIONS.get(msg.business_connection_id)
    return None

# ОБРАБОТКА НОВЫХ СООБЩЕНИЙ
if update.business_message:
    msg = update.business_message
    business_owner_id = get_owner_from_message(msg)
    
    if not business_owner_id:
        logger.warning(f"⚠️ Не найден владелец для сообщения {msg.message_id}")
        return
    
    user_data = load_user_data(business_owner_id)
    key = f"{msg.chat.id}_{msg.message_id}"
    
    # Определяем направление сообщения
    is_from_owner = msg.from_user and msg.from_user.id == business_owner_id
    
    # Обновляем статистику
    if is_from_owner:
        user_data["stats"]["sent"] = user_data["stats"].get("sent", 0) + 1
    else:
        user_data["stats"]["received"] = user_data["stats"].get("received", 0) + 1
    
    message_data = {
        "message_id": msg.message_id,
        "chat_id": msg.chat.id,
        "from_user_id": msg.from_user.id if msg.from_user else None,
        "from_user_name": msg.from_user.full_name if msg.from_user else "Unknown",
        "from_user_username": msg.from_user.username if msg.from_user else None,
        "date": msg.date.isoformat() if msg.date else None,
        "is_from_owner": is_from_owner
    }

    # Сохраняем содержимое
    if msg.text:
        message_data["type"] = "text"
        message_data["text"] = msg.text
    elif msg.photo:
        message_data["type"] = "photo"
        message_data["photo_file_id"] = msg.photo[-1].file_id
        message_data["caption"] = msg.caption
    elif msg.video:
        message_data["type"] = "video"
        message_data["video_file_id"] = msg.video.file_id
        message_data["caption"] = msg.caption
    elif msg.video_note:
        message_data["type"] = "video_note"
        message_data["video_note_file_id"] = msg.video_note.file_id
    elif msg.voice:
        message_data["type"] = "voice"
        message_data["voice_file_id"] = msg.voice.file_id
    elif msg.document:
        message_data["type"] = "document"
        message_data["document_file_id"] = msg.document.file_id
    elif msg.sticker:
        message_data["type"] = "sticker"
        message_data["sticker_file_id"] = msg.sticker.file_id

    user_data["messages"][key] = message_data
    save_user_data(business_owner_id)
    logger.info(f"📥 Сообщение сохранено для пользователя {business_owner_id}")

# ОБРАБОТКА РЕДАКТИРОВАНИЯ СООБЩЕНИЙ
if update.edited_business_message:
    edited_msg = update.edited_business_message
    business_owner_id = get_owner_from_message(edited_msg)
    
    if not business_owner_id:
        logger.warning(f"⚠️ Не найден владелец для редактирования {edited_msg.message_id}")
        return
    
    user_data = load_user_data(business_owner_id)
    key = f"{edited_msg.chat.id}_{edited_msg.message_id}"
    
    old_data = user_data["messages"].get(key, {})
    old_text = old_data.get("text", "N/A")
    new_text = edited_msg.text if edited_msg.text else "N/A"
    
    # Обновляем данные
    if key in user_data["messages"]:
        user_data["messages"][key]["text"] = new_text
        user_data["messages"][key]["edited_at"] = datetime.now().isoformat()
    
    save_user_data(business_owner_id)
    
    # Отправляем уведомление
    username = f"@{edited_msg.from_user.username}" if edited_msg.from_user.username else edited_msg.from_user.full_name
    user_id_str = edited_msg.from_user.id if edited_msg.from_user else "Unknown"
    
    send_date = format_datetime(old_data.get("date"))
    edit_date = datetime.now().strftime("%d.%m.%Y %H:%M")
    
    # Экранируем текст
    old_escaped = escape_markdown(old_text)
    new_escaped = escape_markdown(new_text)
    username_escaped = escape_markdown(username)
    
    alert = f"{username_escaped} \\| ID: `{user_id_str}`\n"
    alert += f"Дата отправки: `{send_date}`\n"
    alert += f"Дата редактирования: `{edit_date}`\n\n"
    alert += f"*Отредактировал сообщение*\n\n"
    alert += f"Было:\n`{old_escaped}`\n\n"
    alert += f"Стало:\n`{new_escaped}`"
    
    try:
        await context.bot.send_message(business_owner_id, alert, parse_mode='MarkdownV2')
        logger.info(f"✅ Редактирование отправлено пользователю {business_owner_id}")
    except Exception as e:
        logger.error(f"❌ Ошибка отправки редактирования: {e}")

# ОБРАБОТКА УДАЛЕНИЙ
if update.deleted_business_messages:
    deleted_msgs = update.deleted_business_messages
    
    # Пытаемся найти владельца через business_connection_id
    business_owner_id = None
    if hasattr(deleted_msgs, 'business_connection_id'):
        business_owner_id = BUSINESS_CONNECTIONS.get(deleted_msgs.business_connection_id)
    
    if not business_owner_id:
        # Ищем владельца по chat_id в сохраненных сообщениях
        for user_id, data in USER_DATA.items():
            for key in data.get("messages", {}).keys():
                if key.startswith(f"{deleted_msgs.chat.id}_"):
                    business_owner_id = user_id
                    break
            if business_owner_id:
                break
    
    if not business_owner_id:
        logger.warning(f"⚠️ Не найден владелец для удаления в чате {deleted_msgs.chat.id}")
        return
    
    user_data = load_user_data(business_owner_id)
    
    for msg_id in deleted_msgs.message_ids:
        key = f"{deleted_msgs.chat.id}_{msg_id}"
        
        if key in user_data["messages"]:
            deleted_data = user_data["messages"][key]
            
            # Определяем, кто удалил
            username = f"@{deleted_data.get('from_user_username')}" if deleted_data.get('from_user_username') else deleted_data.get('from_user_name', 'Unknown')
            user_id_str = deleted_data.get('from_user_id', 'Unknown')
            
            send_date = format_datetime(deleted_data.get("date"))
            delete_date = datetime.now().strftime("%d.%m.%Y %H:%M")
            
            # Экранируем
            username_escaped = escape_markdown(username)
            
            alert = f"{username_escaped} \\| ID: `{user_id_str}`\n"
            alert += f"Дата отправки: `{send_date}`\n"
            alert += f"Дата удаления: `{delete_date}`\n\n"
            alert += f"*Удалил сообщение*\n\n"
            
            if deleted_data.get('type') == 'text':
                text = deleted_data.get('text', 'N/A')
                text_escaped = escape_markdown(text)
                alert += f"Текст:\n`{text_escaped}`"
            
            try:
                await context.bot.send_message(business_owner_id, alert, parse_mode='MarkdownV2')
                
                # Отправляем медиа
                if deleted_data.get('photo_file_id'):
                    await context.bot.send_photo(business_owner_id, deleted_data['photo_file_id'])
                elif deleted_data.get('video_file_id'):
                    await context.bot.send_video(business_owner_id, deleted_data['video_file_id'])
                elif deleted_data.get('voice_file_id'):
                    await context.bot.send_voice(business_owner_id, deleted_data['voice_file_id'])
                elif deleted_data.get('document_file_id'):
                    await context.bot.send_document(business_owner_id, deleted_data['document_file_id'])
                
                logger.info(f"✅ Удаление отправлено пользователю {business_owner_id}")
            except Exception as e:
                logger.error(f"❌ Ошибка отправки удаления: {e}")

# VIEW ONCE при ответе
if update.business_message and update.business_message.reply_to_message:
    replied = update.business_message.reply_to_message
    business_owner_id = get_owner_from_message(update.business_message)
    
    if not business_owner_id:
        return
    
    if replied.photo or replied.video or replied.video_note:
        media_type = "photo" if replied.photo else "video" if replied.video else "video_note"
        await save_view_once(replied, context, business_owner_id, media_type)
```

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
“”“Глобальный обработчик ошибок”””
logger.error(f”❌ Ошибка: {context.error}”)

async def main():
“”“Главная функция”””
app = ApplicationBuilder().token(BOT_TOKEN).build()

```
# Команды
app.add_handler(CommandHandler("start", start_command))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("stats", stats_command))
app.add_handler(TypeHandler(Update, handle_all_updates))
app.add_error_handler(error_handler)

logger.info("="*50)
logger.info("🚀 БОТ ЗАПУСКАЕТСЯ (МУЛЬТИПОЛЬЗОВАТЕЛЬСКИЙ)")
logger.info(f"📁 Папка данных: {DATA_DIR.absolute()}")
logger.info(f"📁 Медиа: {MEDIA_DIR.absolute()}")
logger.info("="*50)

await app.initialize()
await app.start()
await app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
logger.info("✅ БОТ РАБОТАЕТ!")

try:
    while True:
        await asyncio.sleep(1)
except KeyboardInterrupt:
    logger.info("🛑 ОСТАНОВКА...")
    await app.updater.stop()
    await app.stop()
    await app.shutdown()
    logger.info("👋 БОТ ОСТАНОВЛЕН")
```

if **name** == “**main**”:
try:
asyncio.run(main())
except Exception as e:
logger.error(f”💥 КРИТИЧЕСКАЯ ОШИБКА: {e}”)
raise
