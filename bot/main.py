import telebot
from model.main import RecognitionModel

bot = telebot.TeleBot("")
model = RecognitionModel()

def handle_wrong_input(message):
     bot.send_message(message.chat.id, 'Бот принимает изображения форматов bmp, jpeg, png.\nВы можете посмотреть информацию по работе бота с помощью команды help.')

# Handles all text messages that contains the commands '/start' or '/help'.
@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
	bot.send_message(message.chat.id, text = '''Привет!\nЭтот бот создан для распознавания объектов на изображениях. Вы можете прислать ему изображение и получить информацию об объектах на изображении\nХарактеристики модели:
модель - faster rcnn, backbone - resnet50\nвеса - стандартные\nподдерживает изображения различных форматов, включая BMP, JPEG, PNG''')

# Handles all sent documents and audio files
@bot.message_handler(content_types=['photo'])
def handle_docs_photos(message):
    fileID = message.photo[-1].file_id
    file_info = bot.get_file(fileID)
    print(file_info.file_path)
    downloaded_file = bot.download_file(file_info.file_path)
    img, info = model.procces_image(downloaded_file)
    bot.send_photo(message.chat.id, img)
    bot.send_message(message.chat.id, info)

# Handles all sent documents and audio files
@bot.message_handler(content_types=['document'])
def handle_docs_bmp(message):
    fileID = message.document.file_id
    file_info = bot.get_file(fileID)
    downloaded_file = bot.download_file(file_info.file_path)
    img, info = model.procces_image(downloaded_file)
    bot.send_photo(message.chat.id, img)
    bot.send_message(message.chat.id, info)
    bot.send_document(message.chat.id, img, visible_file_name = "{}-marked.{}".format(message.document.file_name.split('.')[0], message.document.file_name.split('.')[1]))
    
@bot.message_handler(content_types=["text", "sticker", "animation", "photo", "audio"])
def handle_rest(message):
    bot.send_animation(
        message.chat.id, "https://media.giphy.com/media/11c7UUfN4eoHF6/giphy.gif"
    )

bot.polling(none_stop=True)
