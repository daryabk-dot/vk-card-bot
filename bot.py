import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
import logging
from PIL import Image, ImageDraw, ImageFont
import io
import requests
import time

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CardBot:
    def __init__(self, group_id, token):
        self.vk_session = vk_api.VkApi(token=token)
        self.vk = self.vk_session.get_api()
        self.longpoll = VkBotLongPoll(self.vk_session, group_id, wait=25)
        
    def run(self):
        logger.info("Бот запущен!")
        while True:
            try:
                for event in self.longpoll.listen():
                    if event.type == VkBotEventType.MESSAGE_NEW:
                        self.handle_message(event)
            except Exception as e:
                logger.error(f"Ошибка: {e}")
                time.sleep(5)
    
    def handle_message(self, event):
        message = event.object.message['text']
        user_id = event.object.message['from_id']
        
        if message.lower() in ['начать', 'старт', 'привет']:
            self.send_welcome(user_id)
        elif 'открытка' in message.lower():
            self.create_card(user_id)
        else:
            self.send_instructions(user_id)
    
    def send_welcome(self, user_id):
        welcome_text = """
        🎉 Привет! Я бот для создания открыток ко Дню Матери!
        
        Напишите "Открытка", чтобы получить красивую открытку для мамы!
        """
        self.send_message(user_id, welcome_text)
    
    def create_card(self, user_id):
        try:
            # Создаем простую открытку
            image = self.generate_simple_card()
            
            # Конвертируем в bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Загружаем на сервер ВК
            upload_url = self.vk.photos.getMessagesUploadServer()['upload_url']
            upload_data = requests.post(upload_url, files={'photo': ('card.png', img_byte_arr)}).json()
            save_data = self.vk.photos.saveMessagesPhoto(
                server=upload_data['server'],
                photo=upload_data['photo'],
                hash=upload_data['hash']
            )
            
            # Получаем attachment
            photo_id = f"photo{save_data[0]['owner_id']}_{save_data[0]['id']}"
            
            # Отправляем пользователю
            self.vk.messages.send(
                user_id=user_id,
                attachment=photo_id,
                message="Ваша открытка готова! Перешлите её маме! 💖",
                random_id=get_random_id()
            )
            
        except Exception as e:
            logger.error(f"Ошибка создания открытки: {e}")
            self.send_message(user_id, "Извините, произошла ошибка 😔")
    
    def generate_simple_card(self):
        """Создает простую открытку"""
        width, height = 800, 600
        image = Image.new('RGB', (width, height), color='#FFE4E1')
        draw = ImageDraw.Draw(image)
        
        # Рисуем текст
        try:
            # Попробуем использовать стандартный шрифт
            font = ImageFont.load_default()
            font_size = 20
        except:
            font = None
        
        # Основной текст
        texts = [
            "С ДНЁМ МАТЕРИ!",
            "Любимой мамочке",
            "Спасибо за всё!",
            "Ты самая лучшая! 💖"
        ]
        
        y_position = 150
        for text in texts:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) / 2
            draw.text((x, y_position), text, fill='#8B008B', font=font)
            y_position += 60
        
        # Рисуем сердечко
        draw.ellipse([300, 400, 350, 450], fill='#FF69B4', outline='#FF1493')
        draw.ellipse([325, 400, 375, 450], fill='#FF69B4', outline='#FF1493')
        draw.polygon([300, 425, 375, 425, 337, 475], fill='#FF69B4')
        
        return image
    
    def send_instructions(self, user_id):
        self.send_message(user_id, "Напишите 'Открытка', чтобы создать открытку для мамы! 🎨")
    
    def send_message(self, user_id, text):
        self.vk.messages.send(
            user_id=user_id,
            message=text,
            random_id=get_random_id()
        )

def main():
    # ЗАМЕНИТЕ эти значения на свои!
    GROUP_ID = '123456789'  # ID вашей группы ВК
    GROUP_TOKEN = 'vk1.a.ваш_токен_здесь'  # Токен группы
    
    bot = CardBot(GROUP_ID, GROUP_TOKEN)
    bot.run()

if __name__ == "__main__":
    main()
