import trio
import trio_asyncio
from quart import render_template, request, websocket
from quart_trio import QuartTrio
from sms_center_api import request_smsc_mocked
import logging
from db import Database
import aioredis
from trio_asyncio import aio_as_trio
from hypercorn.trio import serve
from hypercorn.config import Config as HyperConfig
import warnings

app = QuartTrio(__name__)

STATUS = [{}]


@app.route('/')
async def index():
    return await render_template('index.html')


@app.route('/send/', methods=["POST"])
async def send_message():

    form = await request.form
    text = form['text']

    if not text:
        logging.info('Отправлено пустое сообщение!')
        return await render_template('index.html')

    payload = {
        'phones': '+79165801273',
        'mes': text
    }

    sms_center_login = app.config['sms_center_login']
    sms_center_password = app.config['sms_center_password']

    message = await request_smsc_mocked('POST', 'send', payload, sms_center_login, sms_center_password)

    logging.info(f'Отправлено сообщение с текстом {text}!')

    redis_db = app.config['redis_db']
    await aio_as_trio(redis_db.add_sms_mailing)(message['id'], payload['phones'], payload['mes'])
    return await render_template('index.html')


@app.websocket('/ws')
async def receive_information():

    redis_db = app.config['redis_db']
    while True:
        sms_ids = await aio_as_trio(redis_db.list_sms_mailings)()
        mailings = await aio_as_trio(redis_db.get_sms_mailings)(*sms_ids)

        message = {
            "msgType": "SMSMailingStatus",
            "SMSMailings": []
        }

        for mailing in mailings:
            message['SMSMailings'].append(
                {
                    "timestamp": mailing['created_at'],
                    "SMSText": mailing['text'],
                    "mailingId": str(mailing['sms_id']),
                    "totalSMSAmount": 1,
                    "deliveredSMSAmount": 0,
                    "failedSMSAmount": 0,
                },
            )

        await websocket.send_json(message)
        await trio.sleep(3)


async def run_server():
    warnings.filterwarnings('ignore')

    async with trio_asyncio.open_loop() as loop:
        redis = aioredis.from_url('redis://default:Q8hcmjphF3UTBoDQZzsNVRCn9HhcpdJv@redis-12681.c11.us-east-1-3.ec2.cloud.redislabs.com:12681', decode_responses=True)
        try:
            redis_db = Database(redis)
            config = HyperConfig()
            config.bind = [f"127.0.0.1:5000"]
            config.use_reloader = True

            app.config['sms_center_login'] = 'devman'
            app.config['sms_center_password'] = 'Ab6Kinhyxquot'
            app.config['redis_db'] = redis_db

            logging.basicConfig(level=logging.INFO)

            await serve(app, config)
        finally:
            await redis.close()


if __name__ == '__main__':

    trio_asyncio.run(run_server)
