from aiohttp import web
import asyncio


async def handle(request):
    await asyncio.sleep(1)  # 模拟耗时操作
    return web.Response(text="Hello, world")


app = web.Application()
app.router.add_get('/', handle)

web.run_app(app)
