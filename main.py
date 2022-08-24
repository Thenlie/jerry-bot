import discord
import re
import os
import requests
import json
bot_token = os.environ['TOKEN']
setlist_token = os.environ['SETLIST_KEY']
prefix = 'j!'

def validate_date(date):
    valid_format = re.search('^[0-9]{2}-[0-9]{2}-[0-9]{4}', date)
    year = re.findall('[0-9]{4}', date)[0]
    month = re.findall('[0-9]{2}', date)[0]
    day = re.findall('[0-9]{2}', date)[1]
    if not valid_format:
        return { 'error': 'Invalid date format' }
    if int(year) < 1965 or int(year) > 2022:
        return { 'error': 'Date out of range' }
    print(year, day, month)
    return { 'date': day + '-' + month + '-' + year }
    

def get_show(date: str):
    url = 'https://api.setlist.fm/rest/1.0/search/setlists?artistName=grateful%20dead&date=' + date + 'p=1'
    headers = {'Accept': 'application/json', 'x-api-key': setlist_token}
    response = requests.get(url, headers=headers)
    json_data = json.loads(response.text)
    show_loc = json_data['setlist'][0]['venue']['name']
    # sets = json_data['setlist'][0]['sets']
    set_one = json_data['setlist'][0]['sets']['set'][0]['song']
    set_two = json_data['setlist'][0]['sets']['set'][1]['song']
    setlist = []
    for i in set_one:
        setlist.append(i['name'])
    for i in set_two:
        setlist.append(i['name'])
    # print(sets)
    print(show_loc)
    print(setlist)

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
                embd = discord.Embed(title='Command Error!', description='Please add a command after the bot prefix!', color=0xAB0C0C)
                await message.channel.send(embed=embd)
                return
                
            if args[1] == 'help':
                embd = discord.Embed(title='Jerry Bot Help', description='A full list of commands can be seen below', color=0x3467EB)
                embd.add_field(name='`info`', value='Information about Jerry Bot', inline=False)
                await message.channel.send(embed=embd)
                return
                
            elif args[1] == 'info':
                embd = discord.Embed(title='Jerry Bot Information', description='Created by Thenlie, 2022', color=0x3467EB)
                embd.add_field(name='Language', value='Python', inline=False)
                embd.add_field(name='Repository', value='https://github.com/Thenlie/jerry-bot', inline=False)
                await message.channel.send(embed=embd)
                return
                
            elif args[1] == 'prefix':
                if len(args) == 2:
                    embd = discord.Embed(title='Jerry Bot Prefix', description='Your server\'s prefix is `{0}`. \n Use `{0} prefix help` for a prefix help.'.format(prefix), color=0x3467EB)
                    await message.channel.send(embed=embd)
                    return
                elif args[2] == 'help':
                    embd = discord.Embed(title='Prefix Help', description='A full list of commands can be seen below', color=0x3467EB)
                    embd.add_field(name='`help`', value='List of prefix commands. `{0} prefix help`'.format(prefix), inline=False)
                    embd.add_field(name='`set`', value='Set a new prefix. `{0} prefix set [new-prexif]`'.format(prefix), inline=False)
                    await message.channel.send(embed=embd)
                    return
                elif args[2] == 'set':
                    if len(args) > 4: # argument check
                        embd = discord.Embed(title='Command Error!', description='Too many arguments! Use `{0} prefix help` for help with this command.'.format(prefix), color=0xAB0C0C)
                        await message.channel.send(embed=embd)
                        return
                    else:
                        prefix = args[3]
                        embd = discord.Embed(title='Prefix update successful!', description='Your server\'s prefix is `{0}`'.format(prefix), color=0x3467EB)
                        await message.channel.send(embed=embd)
                    return
                    
            elif args[1] == 'show':
                if len(args) > 3:
                    embd = discord.Embed(title='Command Error!', description='Too many arguments! Use `{0} show help` for help with this command.'.format(prefix), color=0xAB0C0C)
                    await message.channel.send(embed=embd)
                    return
                # valid_data = re.search('^{2}[0-9]-{2}[0-9]-{4}[0-9]', args[3])
                is_valid = validate_date(args[2])
                if 'error' in is_valid:
                    embd = discord.Embed(title='Command Error!', description=is_valid['error'] + ' Use `{0} show help` for help with this command.'.format(prefix), color=0xAB0C0C)
                    await message.channel.send(embed=embd)
                    return
                else:
                    print(is_valid['date'])
                    get_show(is_valid['date'])
                    return
                return
            

intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(bot_token)