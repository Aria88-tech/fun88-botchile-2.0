import os
import logging
from telegram import Update, ChatMember
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    ChatMemberHandler,
)
import openai
import asyncio

# Si usas Jupyter u otro entorno que ya tenga event loop corriendo, descomenta la línea siguiente
# import nest_asyncio; nest_asyncio.apply()

# Configura la API key de OpenAI y el token de Telegram bot desde variables de entorno
openai.api_key = os.getenv("OPENAI_API_KEY")
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Configura logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WELCOME_MESSAGE = """
🙌 ¡Qué bueno tenerte aquí!
Este grupo es para jugadores que quieren aprovechar todos los beneficios de Fun88 Chile.
💬 Comparte tus jugadas
🎁 Reclama tus bonos
📲 Revisa nuestras promociones: https://www.fun88chile.com/promotions

Para empezar, dime: ¿Qué tipo de bonos te gustan más?
🎰 Tragamonedas / ⚽ Deportes / 🃏 Casino en Vivo
"""

RESPUESTAS = {
    "cómo deposito": """💰 ¿Cómo hacer un depósito en Fun88?

1. Inicia sesión en tu cuenta.
2. Haz clic en “Depósito”.
3. Elige tu método de pago.
4. Ingresa el monto (mínimo $1.000 CLP).
5. Confirma y listo. ¡Empieza a jugar!""",
    "cómo retiro": """🏦 ¿Cómo retirar tus ganancias?

1. Inicia sesión en tu cuenta.
2. Haz clic en “Mi cuenta” > “Retirar”.
3. Elige tu método (el mismo con el que depositaste).
4. Ingresa monto (máximo $9.000.000 CLP).
5. Confirma y espera aprobación.""",
    "bono": "🎁 Puedes revisar los bonos disponibles aquí: https://www.fun88chile.com/promotions",
}

# Handler para /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_MESSAGE)

# Handler para responder texto con respuestas predefinidas o IA
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = update.message.text.lower()

    for clave, respuesta in RESPUESTAS.items():
        if clave in mensaje:
            await update.message.reply_text(respuesta)
            return

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Actúa como asistente de soporte de Fun88 Chile."},
                {"role": "user", "content": mensaje}
            ],
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.7,
        )
        reply = response.choices[0].message.content
        await update.message.reply_text(reply)
    except Exception as e:
        logger.error(f"Error con OpenAI: {e}")
        await update.message.reply_text("Lo siento, no puedo responder eso ahora.")

# Handler para saludar nuevos miembros
async def greet_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.chat_member.new_chat_members:
        for member in update.chat_member.new_chat_members:
            # Ignora bots si quieres:
            if member.is_bot:
                continue
            await context.bot.send_message(
                chat_id=update.chat_member.chat.id,
                text=f"¡Hola {member.full_name}! {WELCOME_MESSAGE}"
            )

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), responder))
    app.add_handler(ChatMemberHandler(greet_new_member, ChatMemberHandler.CHAT_MEMBER))

    logger.info("Bot iniciado con éxito.")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    import nest_asyncio

    nest_asyncio.apply()
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()

