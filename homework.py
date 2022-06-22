"""Homework API Telegram-bot."""
import telegram
import exceptions
import time
import logging
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RETRY_TIME = 6
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Send a status."""
    bot.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        text=message
    )


def get_api_answer(current_timestamp) -> dict:
    """Get a response from the request."""
    timestamp = current_timestamp or int(time.time())
    logging.info('Начат запрос к API.')
    data = {
        'headers': HEADERS,
        'params': {'from_date': timestamp}
    }
    try:
        response = requests.get(ENDPOINT, **data)
    except requests.ConnectionError as err:
        raise exceptions.SomethingWentWrong(
            f'Ошибка соединения: {err}') from err
    if response.status_code != 200:
        raise exceptions.SomethingWentWrong('Ресурс недоступен')
    return response.json()


def check_response(response) -> list:
    """Check if response is correct."""
    type_is_correct = isinstance(response, dict)
    dict_is_not_empty = True
    if not response:
        dict_is_not_empty = False
    homeworks_is_list = isinstance(response['homeworks'], list)

    if not type_is_correct:
        raise exceptions.SomethingWentWrong('Ответ не является словарём.')
    if not dict_is_not_empty:
        raise exceptions.SomethingWentWrong('Словарь пуст.')
    if not homeworks_is_list:
        raise exceptions.SomethingWentWrong('Нет списка домашних работ.')
    return response['homeworks']


def parse_status(homework) -> str:
    """Parse the last homework and return its status to send to Telegram."""
    try:
        homework_name = homework['homework_name']
        homework_status = homework['status']
    except KeyError as err:
        raise KeyError(f'Ошибка в поиске значения: {err}')
    else:
        verdict = HOMEWORK_VERDICTS[homework_status]
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens() -> bool:
    """Check if variables exist in local environment."""
    TOKENS = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    return all(TOKENS)


def main():
    """Run the main logic."""
    if check_tokens:
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
    else:
        error_message = (
            """Отсутствует одна из или все обязательные переменные окружения: '
            'PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID. '
            'Программа принудительно остановлена."""
        )
        logging.critical(error_message)
        sys.exit(error_message)
    current_timestamp = int(time.time())
    last_response = ''
    while True:
        try:
            response = get_api_answer(current_timestamp)
            current_timestamp = response['current_date']
            homework = check_response(response)
            if not homework:
                message = 'Нет домашних работ'
                logging.info(message)
                result = message
                if result != last_response:
                    send_message(bot, result)
                    last_response = result
                    logging.info(f'Успешно отправлено сообщение "{result}"')
                continue
            result = parse_status(homework[0])
            if result != last_response:
                send_message(bot, result)
                last_response = result
                logging.info(f'Успешно отправлено сообщение "{result}"')
            else:
                logging.debug('Новые сообщения отсутствуют')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
            logging.error(message)
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    log_format = (
        '%(asctime)s: %(name)s  [%(levelname)s] %(message)s'
    )
    log_file = os.path.join(BASE_DIR, 'output.log')
    log_stream = sys.stdout
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(log_stream)
        ]
    )
    main()
