import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

logging.basicConfig(level=logging.INFO)

NAME, SERVICE, PROJECT, BUDGET, DEADLINE, CONTACT = range(6)

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎬 Our Work", callback_data="work"),
         InlineKeyboardButton("🎨 Services", callback_data="services")],
        [InlineKeyboardButton("🤝 Collaborate", callback_data="collab"),
         InlineKeyboardButton("📸 BTS", callback_data="bts")],
        [InlineKeyboardButton("ℹ️ About SPECTRA", callback_data="about"),
         InlineKeyboardButton("📩 Contact Us", callback_data="contact")],
        [InlineKeyboardButton("📱 Instagram", url="https://www.instagram.com/speccreatives/")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "◇ S P E C T R A\n\n"
        "CREATES ART\n"
        "Visuals | Films | Culture\n\n"
        "◇ Made to be remembered."
    )
    await update.message.reply_text(text, reply_markup=main_menu())

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "collab":
        await q.message.reply_text("🤝 COLLABORATE WITH SPECTRA\n\nWhat should we call you?")
        return NAME

    texts = {
        "work": "🎬 OUR WORK\n\nSelected visuals, films and creative projects.\n\nPortfolio will be added here.",
        "services": "🎨 SERVICES\n\n• Film & Video Production\n• Creative Visuals\n• Photography\n• Social Media Content\n• Brand Collaborations",
        "bts": "📸 BTS\n\nBehind-the-scenes content will be added here.",
        "about": "ℹ️ ABOUT SPECTRA\n\nSPECTRA is a creative space focused on visuals, films and culture.\n\nMade to be remembered.",
        "contact": "📩 CONTACT US\n\nUse 'Collaborate' to send a project enquiry."
    }
    await q.message.reply_text(texts.get(q.data, "SPECTRA"), reply_markup=main_menu())

async def get_name(update, context):
    context.user_data["name"] = update.message.text
    keyboard = [
        [InlineKeyboardButton("🎥 Film / Video", callback_data="Film / Video")],
        [InlineKeyboardButton("🎨 Visual Design", callback_data="Visual Design")],
        [InlineKeyboardButton("📸 Photography", callback_data="Photography")],
        [InlineKeyboardButton("📱 Social Content", callback_data="Social Content")],
        [InlineKeyboardButton("🤝 Brand Collaboration", callback_data="Brand Collaboration")],
        [InlineKeyboardButton("✨ Other", callback_data="Other")]
    ]
    await update.message.reply_text("What do you need help with?", reply_markup=InlineKeyboardMarkup(keyboard))
    return SERVICE

async def get_service(update, context):
    q = update.callback_query
    await q.answer()
    context.user_data["service"] = q.data
    await q.message.reply_text("📝 Tell us briefly about your project.")
    return PROJECT

async def get_project(update, context):
    context.user_data["project"] = update.message.text
    await update.message.reply_text("💰 What is your approximate budget?")
    return BUDGET

async def get_budget(update, context):
    context.user_data["budget"] = update.message.text
    await update.message.reply_text("📅 What is your deadline?")
    return DEADLINE

async def get_deadline(update, context):
    context.user_data["deadline"] = update.message.text
    await update.message.reply_text("📞 How can SPECTRA contact you? (Instagram/WhatsApp/Telegram)")
    return CONTACT

async def get_contact(update, context):
    context.user_data["contact"] = update.message.text
    d = context.user_data
    summary = (
        "🔔 NEW SPECTRA COLLABORATION\n\n"
        f"👤 Name: {d['name']}\n"
        f"🎯 Service: {d['service']}\n"
        f"📝 Project: {d['project']}\n"
        f"💰 Budget: {d['budget']}\n"
        f"📅 Deadline: {d['deadline']}\n"
        f"📞 Contact: {d['contact']}"
    )
    if ADMIN_CHAT_ID:
        try:
            await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=summary)
        except Exception:
            logging.exception("Admin notification failed")
    await update.message.reply_text(
        "◇ THANK YOU\n\nYour project enquiry has been received by SPECTRA.\nWe'll get back to you soon. 🎬",
        reply_markup=main_menu()
    )
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update, context):
    context.user_data.clear()
    await update.message.reply_text("Cancelled. Back to SPECTRA.", reply_markup=main_menu())
    return ConversationHandler.END

def build_app():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN environment variable is missing.")
    app = Application.builder().token(TOKEN).build()
    conversation = ConversationHandler(
        entry_points=[CallbackQueryHandler(menu, pattern="^collab$")],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            SERVICE: [CallbackQueryHandler(get_service)],
            PROJECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_project)],
            BUDGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_budget)],
            DEADLINE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_deadline)],
            CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_contact)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(conversation)
    app.add_handler(CallbackQueryHandler(menu))
    return app

if __name__ == "__main__":
    build_app().run_polling()
