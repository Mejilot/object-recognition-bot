import telebot
from model.recognition_model import RecognitionModel

# view слой в виде класса Tbot, view - model связка, не mvc


class TBot:
    def __init__(self, env_key):
        self.model = RecognitionModel()
        self.bot = telebot.TeleBot(env_key)

        # обработчик команд start help
        @self.bot.message_handler(commands=['start', 'help'])
        def handle_start_help(message):
            self.bot.send_message(message.chat.id, text='''Привет!\nЭтот бот создан для распознавания объектов на изображениях. Вы можете прислать ему изображение и получить информацию об объектах на изображении\nХарактеристики модели:
        модель - faster rcnn, backbone - resnet50\nвеса - стандартные\nподдерживает изображения различных форматов, включая BMP, JPEG, PNG''')

        # обработчик для изображений присылаемых quick format с сжатием
        @self.bot.message_handler(content_types=['photo'])
        def handle_docs_photos(message):
            print('Handling photo')
            # не стал обрабатывать несколько фото в одном сообщении, беру последнее
            file_id = message.photo[-1].file_id
            file_info = self.bot.get_file(file_id)
            # downloaded_file - изображение в формате bytes()
            downloaded_file = self.bot.download_file(file_info.file_path)
            img, info = self.model.process_image(downloaded_file)
            # изображение с помеченными объектами и список объектов
            self.bot.send_photo(message.chat.id, img)
            self.bot.send_message(message.chat.id, info)

        # обработчик на случай если изображение посылается как документ
        @self.bot.message_handler(content_types=['document'])
        def handle_docs_bmp(message):
            print('Handling document')
            # проверка что присылаемый документ - изображение
            if message.document.mime_type.split('/')[0] != 'image':
                self.handle_wrong_input(message)
                return
            # скачиваю файл изображения
            file_id = message.document.file_id
            file_info = self.bot.get_file(file_id)
            downloaded_file = self.bot.download_file(file_info.file_path)
            # модель обрабатывает изображение
            img, info = self.model.process_image(downloaded_file)
            # отправляю изображение как фото: тут происходит сжатие и потеря качества
            self.bot.send_photo(message.chat.id, img)
            # список объектов на изображении
            self.bot.send_message(message.chat.id, info)
            # отправляю также изображение в несжатом виде
            self.bot.send_document(message.chat.id, img,
                                   visible_file_name="{}-marked.{}".format(message.document.file_name.split('.')[0],
                                                                           message.document.file_name.split('.')[1]))
        # обработчик на все другие сообщения

        @self.bot.message_handler(content_types=["text", "sticker", "animation", "audio"])
        def handle_rest(message):
            self.handle_wrong_input(message)
    # обработка неправильного ввода

    def handle_wrong_input(self, message):
        self.bot.send_message(
            message.chat.id, 'Бот принимает только изображения, если вы запутались - /help'
        )
    # функция запуска бота

    def start_bot(self):
        self.bot.polling(none_stop=True)
