import logging
import asks
import json
from unittest.mock import patch
import asyncclick as click
import sys


async def request_smsc(http_method, api_method, payload, login, password):

    params = {
        'login': login,
        'psw': password,
        'fmt': 3,
        'valid': 1,
        'charset': 'utf-8',
        **payload
    }

    url = f'https://smsc.ru/sys/{api_method}.php'
    response = await asks.request(uri=url, method=http_method, params=params)

    return json.loads(response.text)


async def request_smsc_mocked(http_method, api_method, payload, login, password):

    with patch('sms_center_api.request_smsc') as mock_function:
        mock_function.return_value = {"id": 335, "cnt": 3}
        message = await request_smsc(http_method, api_method, payload, login, password)
    return message


@click.command()
@click.option('-l', '--login', help='Логин аккаунта SMS Центра')
@click.option('-p', '--password', help='Пароль аккаунта SMS Центра')
@click.option('-m', '--message', help='Текст сообщения')
@click.option('-t', '--telephone', help='Номер телефона')
async def main(login, password, message, telephone):

    logging.basicConfig(level=logging.INFO)

    payload = {
        'phones': telephone,
        'mes': message
    }

    logging.info(await request_smsc('POST', 'send', payload, login, password))

if __name__ == '__main__':
    try:
        main(_anyio_backend='trio')
    except KeyboardInterrupt:
        sys.stderr.write('Вы закрыли скрипт')
