from discord_bot import AddressBot
from message_server import start_web_server
import discord
import asyncio
from libs.common import load_environment_variable

token = load_environment_variable('DISCORD_BOT_TOKEN')
intents = discord.Intents.default()
intents.messages = True

async def main():
    bot = AddressBot(intents=intents)
    await start_web_server(bot)  # 启动HTTP服务器
    await bot.start(token)  # 启动Discord机器人

if __name__ == "__main__":
    asyncio.run(main())
