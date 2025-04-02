from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from rembg import remove
from io import BytesIO
from PIL import Image
import os
import asyncio
 #-
TOKEN = os.getenv("BOT_TOKEN")
user_languages = {}
user_backgrounds = {}

LANGUAGES = {
    "ar": ("العربية", "🇩🇿"),
    "en": ("English", "🇬🇧"),
    "fr": ("Français", "🇫🇷")
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(f"{flag} {name}", callback_data=code)]
                for code, (name, flag) in LANGUAGES.items()]
    await update.message.reply_text("مرحباً! اختر اللغة / Choose a language:", reply_markup=InlineKeyboardMarkup(keyboard))

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang_code = query.data
    user_languages[query.from_user.id] = lang_code
    await query.edit_message_text(f"تم اختيار اللغة: {LANGUAGES[lang_code][1]} {LANGUAGES[lang_code][0]}")

async def remove_bg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    lang = user_languages.get(user_id, "ar")
    if not update.message.photo:
        await update.message.reply_text("أرسل صورة من فضلك.")
        return
    msg = await update.message.reply_text("⏳ جاري المعالجة...")

    try:
        photo = await update.message.photo[-1].get_file()
        image_data = await photo.download_as_bytearray()
        img = Image.open(BytesIO(image_data)).convert("RGBA")
        temp = BytesIO(); img.save(temp, format="PNG"); temp.seek(0)
        fg = Image.open(BytesIO(remove(temp.getvalue()))).convert("RGBA")
        result = BytesIO(); fg.save(result, format="PNG"); result.seek(0)
        await msg.delete()
        await update.message.reply_document(document=InputFile(result, filename="no_bg.png"), caption="✅ تمت المعالجة!")
    except Exception as e:
        await msg.edit_text("❌ خطأ في المعالجة.")
        print(e)

async def set_commands(app):
    await app.bot.set_my_commands([
        BotCommand("start", "بدء البوت"),
    ])

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(set_language))
app.add_handler(MessageHandler(filters.PHOTO, remove_bg))

async def main():
    await set_commands(app)
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
