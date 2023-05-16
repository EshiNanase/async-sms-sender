from quart import render_template, websocket
from quart_trio import QuartTrio

app = QuartTrio(__name__)


@app.route('/')
async def index():
    return await render_template('index.html')


if __name__ == '__main__':
    app.run()
