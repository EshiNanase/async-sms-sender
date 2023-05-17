import asks
from contextvars import ContextVar
import json
from unittest.mock import patch

import trio


async def request_smsc(http_method, api_method, payload, login=None, password=None):

    params = {
        'login': login or smsc_login.get(),
        'psw': password or smsc_password.get(),
        'fmt': 3,
        'valid': 1,
        'charset': 'utf-8',
        **payload
    }

    url = f'https://smsc.ru/sys/{api_method}.php'
    response = await asks.request(uri=url, method=http_method, params=params)

    return json.loads(response.text)


async def request_smsc_mocked(http_method, api_method, payload, login=None, password=None):

    with patch('sms_center_api.request_smsc') as mock_function:
        mock_function.return_value = {"id": 335, "cnt": 3}
        message = await request_smsc(http_method, api_method, payload, login, password)
    return message


if __name__ == '__main__':

    smsc_login = ContextVar('sms_center_login')
    smsc_password = ContextVar('sms_center_password')

    smsc_login.set('devman')
    smsc_password.set('Ab6Kinhyxquot')
