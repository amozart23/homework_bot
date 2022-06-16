import requests
import telegram
from pprint import pprint
import datetime
import exceptions
import time
import logging
import os
from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler
from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 6
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level=logging.INFO)


def send_message(bot, message):
    """Send a status."""
    button = ReplyKeyboardMarkup([['/check']], resize_keyboard=True)
    bot.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        text=message,
        reply_markup=button
        )


def get_api_answer(current_timestamp) -> dict:
    """Get a response from the request."""
    timestamp = current_timestamp or int(time.time())
    data = {
        'headers': HEADERS,
        'params': {'from_date': timestamp}
    }
    if requests.get(ENDPOINT, **data).status_code != 200:
        raise exceptions.SomethingWentWrong
    return requests.get(ENDPOINT, **data).json()


def check_response(response):
    """Check if response is correct."""
    type_is_correct = isinstance(response, dict)
    dict_is_not_empty = len(response) > 0
    homeworks_is_list = isinstance(response['homeworks'], list)
    if type_is_correct and dict_is_not_empty and homeworks_is_list:
        return response
    else:
        raise exceptions.SomethingWentWrong


def parse_status(homework) -> str:
    """Parse the last homework and return its status to send to Telegram."""
    try:
        homework_name = homework['homework_name']
        homework_status = homework['status']
        verdict = HOMEWORK_STATUSES[homework_status]
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    except Exception as error:
        logging.error(error)


def check_tokens() -> bool:
    """Check if variables exist in local environment."""
    TOKENS = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    if None in TOKENS:
        return False
    else:
        return True


# При периодических запросах к API можно использовать значение, полученное под ключом current_date, в качестве параметра from_date в следующем запросе.


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    
    my_datetime = datetime.date(2022, 5, 25)
    current_timestamp = int(time.mktime(my_datetime.timetuple()))
    # current_timestamp = int(time.time())
    last_response = ''
    while True:
        try:
            response = get_api_answer(current_timestamp)
            result = parse_status(response['homeworks'][0])
            if result != last_response:
                send_message(bot, result),
                last_response = result
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            time.sleep(RETRY_TIME)
            print(message)
        else:
            pass


if __name__ == '__main__':
    main()
    # my_datetime = datetime.date(2022, 5, 25)
    # print(type(get_api_answer(int(time.mktime(my_datetime.timetuple())))))
    # my_datetime = datetime.date(2022, 5, 25)
    # unix_time = 
    # print(parse_status(get_api_answer(unix_time)))
    # pprint(get_api_answer(unix_time))
