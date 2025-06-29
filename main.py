import os
import logging
import openai
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Carga las claves desde variables de entorno
openai.api_key = os.getenv("OPENAI_API_KEY")
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    print("ERROR: La variable de entorno TELEGRAM_BOT_TOKEN no está configurada o está vacía.")
    exit(1)

if not openai.api_key:
    print("ERROR: La variable de entorno OPENAI_API_KEY no está configurada o está vacía.")
    exit(1)

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_MESSAGE)

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
            ]
        )
        reply = response.choices[0].message.content
        await update.message.reply_text(reply)
    except Exception as e:
        logger.error(f"Error con OpenAI: {e}")
        await update.message.reply_text("Lo siento, no puedo responder eso ahora.")

async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), responder))
    logger.info("Bot iniciado con éxito.")
    await app.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
