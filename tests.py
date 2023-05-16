from unittest.mock import patch
import trio
from sms_center_api import request_smsc


async def test_request_smsc():

    with patch('sms_center_api.request_smsc') as mock:
        mock.return_value = {'!!!!!!!!!!!!!!!!!!!!!!!!!!!!'}
        message = await request_smsc(
            'POST',
            'send',
            {'phones': '+79165801273', 'message': 'привет'},
            'login',
            'password'
        )
        assert mock.return_value == message


trio.run(test_request_smsc)

