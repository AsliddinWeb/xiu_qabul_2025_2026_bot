from telegram import (
    Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Config
import os
from dotenv import load_dotenv

load_dotenv()

# Google Sheets sozlash
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(os.getenv('GOOGLE_CREDENTIALS_PATH'), scope)
client = gspread.authorize(creds)
sheet = client.open("Qabul2025").sheet1

# Holatlar
ASK_NAME, ASK_PHONE, ASK_DIRECTION = range(3)

# Yo‘nalishlar ro‘yxati
directions = [
    "Iqtisodiyot (tarmoqlar va sohalar bo‘yicha)",
    "Buxgalteriya hisobi",
    "Moliya va moliyaviy texnologiyalar",
    "Pedagogika va psixologiya",
    "Pedagogika",
    "Maktabgacha ta’lim",
    "Maxsus pedagogika",
    "Boshlang‘ich ta’lim",
    "Musiqa ta’limi",
    "Psixologiya (faoliyat turlari bo‘yicha)",
    "Matematika",
    "Jismoniy madaniyat",
    "Tarix",
    "Filologiya va tillarni o‘qitish (ingliz tili)",
    "Filologiya va tillarni o‘qitish (rus tili)",
    "Filologiya va tillarni o‘qitish (o‘zbek tili)",
    "Jurnalistika (faoliyat turlari bo‘yicha)",
    "Kutubxona-axborot faoliyati (faoliyat turlari bo‘yicha)",
    "Axborot tizimlari va texnologiyalari (tarmoqlar va sohalar bo‘yicha)",
    "Kommunal infratuzilmani tashkil etish va boshqarish",
    "Yer kadastri va yer tuzish"
]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Assalomu alaykum! Iltimos, ismingiz va familiyangizni kiriting:")
    return ASK_NAME

async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    contact_btn = KeyboardButton("📱 Telefon raqamni yuborish", request_contact=True)
    markup = ReplyKeyboardMarkup([[contact_btn]], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Telefon raqamingizni kiriting yoki yuboring:", reply_markup=markup)
    return ASK_PHONE

async def ask_direction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.contact:
        context.user_data['phone'] = f"+{update.message.contact.phone_number}"
    else:
        context.user_data['phone'] = update.message.text

    # Yo‘nalishlar tugmasi
    buttons = [[KeyboardButton(dir)] for dir in directions]
    markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Qaysi yo‘nalishga qiziqasiz?", reply_markup=markup)
    return ASK_DIRECTION

async def save_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    direction = update.message.text
    context.user_data['direction'] = direction

    # Google Sheets'ga yozish
    sheet.append_row([
        context.user_data['name'],
        context.user_data['phone'],
        context.user_data['direction']
    ])

    await update.message.reply_text("Rahmat! Ma'lumotlaringiz muvaffaqiyatli saqlandi ✅\n\n/start /start /start", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bekor qilindi.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

if __name__ == '__main__':
    app = ApplicationBuilder().token(os.getenv('BOT_TOKEN')).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)],
            ASK_PHONE: [MessageHandler((filters.CONTACT | filters.TEXT) & ~filters.COMMAND, ask_direction)],
            ASK_DIRECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_data)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    app.add_handler(conv_handler)
    print("Bot ishga tushdi...")
    app.run_polling()
