import requests
from pprint import pprint
import datetime
import exceptions
import time
import logging
import os
from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Updater
from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': PRACTICUM_TOKEN}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)


def send_message(bot, message):
    """Send a status."""
    button = ReplyKeyboardMarkup([['/check']], resize_keyboard=True)
    bot.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        text='Привет, {}. Посмотри какого котика я тебе нашел',
        reply_markup=button
        )


def get_api_answer(current_timestamp):
    """Get a response from the request."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    return requests.get(ENDPOINT, headers=HEADERS, params=params).json()


def check_response(response) -> bool:
    """Check if response is correct."""
    type_is_correct = isinstance(response, dict)
    return type_is_correct



def parse_status(homework):
    """
    Функция parse_status() извлекает из информации о конкретной домашней работе статус этой работы.
    В качестве параметра функция получает только один элемент из списка домашних работ.
    В случае успеха, функция возвращает подготовленную для отправки в Telegram строку, содержащую один из вердиктов словаря HOMEWORK_STATUSES.
    """
    homework_name = homework['homework_name']
    homework_status = homework['status']
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens() -> bool:
    """Check if variables exist in local environment."""
    TOKENS = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    if None in TOKENS:
        return False
    else:
        return True


def main():
    """Основная логика работы бота."""
    # bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    try:
        response = get_api_answer(current_timestamp)
        print(parse_status(response))
        time.sleep(RETRY_TIME)
    except Exception as error:
        message = f'Сбой в работе программы: {error}'
        time.sleep(RETRY_TIME)
        print(error)
    else:
        pass


if __name__ == '__main__':
    # main()
    print(parse_status(get_api_answer(int(time.time()))))
