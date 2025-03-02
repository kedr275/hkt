import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_gigachat.chat_models import GigaChat
import promt

TOKEN = ''
AUT_TOKEN = ''

giga = GigaChat(
    credentials=AUT_TOKEN,
    verify_ssl_certs=False,
    model="GigaChat-Pro"
)

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Папка для сохранения файлов
UPLOAD_FOLDER = 'uploads'

# Создаем папку, если она не существует
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Команда /start
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Привет! Отправь мне файл, и я сохраню его. Или просто напиши что-нибудь.')

# Обработка файлов
async def handle_file(update: Update, context: CallbackContext) -> None:
    if update.message.document:
        file = await update.message.document.get_file()
        file_name = update.message.document.file_name
        file_path = os.path.join(UPLOAD_FOLDER, file_name)
        
        # Скачиваем файл
        await file.download_to_drive(file_path)
        
        await update.message.reply_text(f'Файл "{file_name}" успешно сохранен!')
    else:
        await update.message.reply_text('Пожалуйста, отправьте файл.')

# Обработка текстовых сообщений
async def handle_text(update: Update, context: CallbackContext) -> None:
    user_text = update.message.text  # Получаем текст сообщения от пользователя
    pr = promt.pr1 + user_text
    messages = [
        SystemMessage(
            content="Ты архитектор который помогает рисовать структурные схемы в формате xml"
        )
    ]
    messages.append(HumanMessage(content=pr))
    messages.append(HumanMessage(content=user_text))
    res = giga.invoke(messages)
    messages.append(res)
    print("Пользователь: ", promt.pr1)
#    print("Пользователь: ", promt.pr5)
    print("GigaChat: ", res.content)
    mess = res.content

    # Сохраняем ответ в файл
    file_path = os.path.join(UPLOAD_FOLDER, "test.xml")
    with open(file_path, "w") as file:
        file.write(mess)

    # Отправляем файл пользователю
    await update.message.reply_document(document=open(file_path, "rb"))

# Обработка ошибок
async def error(update: Update, context: CallbackContext) -> None:
    logger.warning(f'Update {update} caused error {context.error}')

def main() -> None:
    # Вставьте сюда ваш токен
    token = TOKEN
    
    # Создаем Application и передаем ему токен вашего бота
    application = Application.builder().token(token).build()

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))

    # Регистрируем обработчик файлов
    application.add_handler(MessageHandler(filters.Document.ALL, handle_file))

    # Регистрируем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Регистрируем обработчик ошибок
    application.add_error_handler(error)

    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()
