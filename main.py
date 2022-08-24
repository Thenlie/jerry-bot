import os
import discord
bot_token = os.environ['TOKEN']
prefix = 'j!'

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        global prefix
        if message.author.bot == True: # ignore messages from bots
            return
        if message.content.startswith(prefix + ' '): # prefix check
            args = message.content.split(' ')
            print(args)
            if len(args) < 2: # argument check
                embd = discord.Embed(title="Command Error!", description="Please add a command after the bot prefix!", color=0xAB0C0C)
                await message.channel.send(embed=embd)
                return
            if args[1] == 'help':
                embd = discord.Embed(title="Jerry Bot Help", description="A full list of commands can be seen below", color=0x3467EB)
                embd.add_field(name="`info`", value="Information about Jerry Bot", inline=False)
                await message.channel.send(embed=embd)
                return
            elif args[1] == 'info':
                embd = discord.Embed(title="Jerry Bot Information", description="Created by Thenlie, 2022", color=0x3467EB)
                embd.add_field(name="Language", value="Python", inline=False)
                embd.add_field(name="Repository", value="https://github.com/Thenlie/jerry-bot", inline=False)
                await message.channel.send(embed=embd)
                return
            elif args[1] == 'prefix':
                if len(args) == 2:
                    embd = discord.Embed(title="Jerry Bot Prefix", description="Your server's prefix is `{0}`. \n Use `{0} prefix help` for a prefix help.".format(prefix), color=0x3467EB)
                    await message.channel.send(embed=embd)
                    return
                elif args[2] == 'help':
                    embd = discord.Embed(title="Prefix Help", description="A full list of commands can be seen below", color=0x3467EB)
                    embd.add_field(name="`help`", value="List of prefix commands. `{0} prefix help`".format(prefix), inline=False)
                    embd.add_field(name="`set`", value="Set a new prefix. `{0} prefix set [new-prexif]`".format(prefix), inline=False)
                    await message.channel.send(embed=embd)
                    return
                elif args[2] == 'set':
                    if len(args) > 4:
                        embd = discord.Embed(title="Command Error!", description="Too many arguments! Use `{0} prefix help` for help with this command.".format(prefix), color=0xAB0C0C)
                        await message.channel.send(embed=embd)
                        return
                    else:
                        prefix = args[3]
                        embd = discord.Embed(title="Prefix update successful!", description="Your server's prefix is `{0}`".format(prefix), color=0x3467EB)
                        await message.channel.send(embed=embd)
                    return
            

intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(bot_token)