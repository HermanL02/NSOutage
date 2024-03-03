from aiohttp import web
import json

async def handle_post(request):
    bot = request.app['bot']
    data = await request.json()
    user_id = data.get('user_id')
    message = data.get('message')
    if user_id and message:
        await bot.send_direct_message(user_id, message)
        return web.Response(text="Message sent successfully", status=200)
    return web.Response(text="Bad request", status=400)

async def handle_broadcast(request):
    bot = request.app['bot']
    data = await request.json()
    message = data.get('message')
    if message:
        await bot.broadcast_message_to_all_guilds(message)
        return web.Response(text="Broadcast message sent successfully", status=200)
    return web.Response(text="Bad request", status=400)

async def start_web_server(bot):
    app = web.Application()
    app['bot'] = bot
    app.router.add_post('/send-message', handle_post)  
    app.router.add_post('/broadcast', handle_broadcast)  
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8081)
    await site.start()

