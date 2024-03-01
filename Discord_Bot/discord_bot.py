import asyncio
import os
from dotenv import load_dotenv
import discord
import user_crud
import aiohttp
# Load environment variables
load_dotenv()
token = os.getenv('DISCORD_BOT_TOKEN')
intents = discord.Intents.default()  # 默认的intent包括了大部分非特权事件
intents.messages = True  # 如果你的bot需要读取消息
class AddressBot(discord.Client):
    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
    async def on_message(self, message):
        # Ignore messages sent by the bot itself
        if message.author == self.user:
            return
        print(message.channel, message.author, message.content)
        # Handle commands
        if message.content.startswith('!addaddress'):
            await self.handle_add_address(message)
        elif message.content == 'ping':
            await message.channel.send('pong')
        else:
            if message.content not in ['yes', 'no',"Yes", "No"]:
                if isinstance(message.channel, discord.DMChannel):
                    help_message = """
                    Here are my commands:
                    - `!addaddress`: Adds a new address. Use format: !addaddress [nickname: eg. Home] [address: eg. 1048 Wellington St., Halifax, B3H 0C2].
                    """
                    await message.channel.send(help_message)
    async def send_direct_message(self, user_id, message):
        user = await self.fetch_user(user_id)
        await user.send(message)
    async def handle_add_address(self, message):
        address_name, address = self.parse_address_message(message.content)
        if not address_name or not address:
            await message.channel.send("Please use format: !addaddress [nickname: eg. Home] [address: eg. 1048 Wellington St., Halifax, B3H 0C2].")
            return

        # 使用OpenStreetMap的Nominatim服务搜索地址
        url = f"https://nominatim.openstreetmap.org/search?format=json&q={address}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data:
                        # 假设我们只关心第一个搜索结果
                        full_address = data[0]["display_name"]
                        latitude = data[0]["lat"]
                        longitude = data[0]["lon"]
                        await message.channel.send(f"Is this the correct address: '{full_address}'? Please respond with 'yes' or 'no'.")
                        # 这里我们需要实现等待用户回应的逻辑
                        def check(m):
                            return m.author == message.author and m.content.lower() in ['yes', 'no']
                        
                        try:
                            confirmation = await self.wait_for('message', check=check, timeout=60.0)  # 等待60秒
                            if confirmation.content.lower() == 'yes':
                                user_crud.add_address(message.author.id, address_name, full_address,longitude,latitude)
                                await message.channel.send(f"Address '{address_name}' added successfully for {message.author.name}.")
                            else:
                                await message.channel.send("Address addition cancelled.")
                        except asyncio.TimeoutError:
                            await message.channel.send("Timeout, address addition cancelled.")
                    else:
                        await message.channel.send("Address not found.")
                else:
                    await message.channel.send("Failed to search the address, please try again later.")

    def parse_address_message(self, content):
        parts = content.split(maxsplit=2)
        if len(parts) < 3:
            return None, None, None  # Insufficient arguments
        # Delete [] from the address name
        address_name = parts[1].replace('[', '').replace(']', '')
        address = parts[2].replace('[', '').replace(']', '')
        return address_name, address

def run_bot():
    bot = AddressBot(intents=intents)
    bot.run(token)

if __name__ == "__main__":
    run_bot()
