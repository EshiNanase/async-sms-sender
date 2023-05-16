import asks
import logging
import trio
from contextvars import ContextVar


async def request_smsc(http_method, api_method, payload, login=None, password=None):

    params = {
        'login': login or smsc_login.get(),
        'password': password or smsc_password.get(),
        'fmt': 3,
        **payload
    }

    url = f'https://smsc.ru/sys/{api_method}'
    response = await asks.request(uri=url, method=http_method, params=params)
    logging.info('SMS отправлено!')


async def main():

    payload = {
        'phones': '+79165801273',
        'message': 'привет',
    }
    await request_smsc('POST', 'send', payload)


if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO)
    smsc_login = ContextVar('sms_center_login')
    smsc_password = ContextVar('sms_center_password')

    smsc_login.set('admin')
    smsc_password.set('pass')

    trio.run(main)
