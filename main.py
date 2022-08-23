import os
import discord
bot_token = os.environ['TOKEN']

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        if message.author == client.user:
            return
        if message.content.startswith('j! '):
            # await message.channel.send('This is a test...')
            args = message.content.split(' ')
            print(args)
            if len(args) > 2:
                await message.channel.send('Error! Too many arguments.')
                return
            

intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(bot_token)