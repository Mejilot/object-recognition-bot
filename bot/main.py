import telebot
from model.main import RecognitionModel

class TBot:
    def __init__(self, env_key):
        self.model = RecognitionModel()
        self.bot = telebot.TeleBot(env_key)

        @self.bot.message_handler(commands=['start', 'help'])
        def handle_start_help(message):
            self.bot.send_message(message.chat.id, text = '''Привет!\nЭтот бот создан для распознавания объектов на изображениях. Вы можете прислать ему изображение и получить информацию об объектах на изображении\nХарактеристики модели:
        модель - faster rcnn, backbone - resnet50\nвеса - стандартные\nподдерживает изображения различных форматов, включая BMP, JPEG, PNG''')

        @self.bot.message_handler(content_types=['photo'])
        def handle_docs_photos(message):
            file_id = message.photo[-1].file_id
            file_info = self.bot.get_file(file_id)
            downloaded_file = self.bot.download_file(file_info.file_path)
            img, info = self.model.process_image(downloaded_file)
            self.bot.send_photo(message.chat.id, img)
            self.bot.send_message(message.chat.id, info)

        # Handles all sent documents and audio files
        @self.bot.message_handler(content_types=['document'])
        def handle_docs_bmp(message):
            file_id = message.document.file_id
            file_info = self.bot.get_file(file_id)
            downloaded_file = self.bot.download_file(file_info.file_path)
            img, info = self.model.process_image(downloaded_file)
            self.bot.send_photo(message.chat.id, img)
            self.bot.send_message(message.chat.id, info)
            self.bot.send_document(message.chat.id, img,
                                   visible_file_name = "{}-marked.{}".format(message.document.file_name.split('.')[0],
                                                                             message.document.file_name.split('.')[1]))

        @self.bot.message_handler(content_types=["text", "sticker", "animation", "audio"])
        def handle_rest(message):
            self.bot.send_message(
                message.chat.id, 'Бот принимает только изображения, если вы запутались -  /help'
            )
    def start_bot(self):
        self.bot.polling(none_stop=True)
