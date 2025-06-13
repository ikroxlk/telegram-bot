from telegram import Update, ChatPermissions
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
)
import re
from datetime import datetime, timedelta
import json
import os

BOT_TOKEN = "7901696673:AAH4MECyq9vHvGUOEnIfDtbv_BRu-LPm_WM"
OWNER_ID = 7018322621  # Replace this with your Telegram user ID

WARNING_FILE = "warnings.json"

def load_warnings():
    if os.path.exists(WARNING_FILE):
        with open(WARNING_FILE, "r") as f:
            return json.load(f)
    return {}

def save_warnings(data):
    with open(WARNING_FILE, "w") as f:
        json.dump(data, f)

user_link_warnings = load_warnings()

def contains_link(text):
    return bool(re.search(r"(https?://|www\.)", text))

def get_user_display(user):
    if user.username:
        return f"@{user.username}"
    elif user.full_name:
        return user.full_name
    else:
        return f"UserID: {user.id}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    if user is None or user.is_bot:
        return

    user_id = str(user.id)
    user_display = get_user_display(user)

    if message.text and contains_link(message.text):
        try:
            await message.delete()
        except Exception as e:
            print(f"Delete failed: {e}")

        try:
            await chat.send_message("ලින්ක් දාන්න එපා උට්ටෝ", reply_to_message_id=message.message_id)
        except Exception as e:
            print(f"Warning failed: {e}")

        count = user_link_warnings.get(user_id, 0) + 1
        user_link_warnings[user_id] = count
        save_warnings(user_link_warnings)

        if count >= 3:
            until_date = datetime.utcnow() + timedelta(weeks=1)
            permissions = ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_polls=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False,
                can_change_info=False,
                can_invite_users=False,
                can_pin_messages=False,
            )
            try:
                await context.bot.restrict_chat_member(
                    chat_id=chat.id,
                    user_id=int(user_id),
                    permissions=permissions,
                    until_date=until_date,
                )
                await chat.send_message(
                    f"{user_display} ලින්ක් තවත් දාන්න එපා. දැන් text දාන්න බෑ සතියක්."
                )
            except Exception as e:
                print(f"Restrict failed: {e}")
        return

    if message.photo or message.video or message.document or message.audio:
        try:
            caption = f"📥 Media from {user_display} (ID: {user_id})"
            await context.bot.send_message(chat_id=OWNER_ID, text=caption)
            await message.forward(chat_id=OWNER_ID)
        except Exception as e:
            print(f"Media forward failed: {e}")

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, handle_message))
    print("Bot is running...")
    await app.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
