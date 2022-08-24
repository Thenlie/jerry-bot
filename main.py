import discord
import re
import os
import requests
import json
bot_token = os.environ['TOKEN']
setlist_token = os.environ['SETLIST_KEY']
prefix = 'j!'

def validate_date(date):
    valid_format = re.search('^[0-9]{2}[-/.][0-9]{2}[./-][0-9]{4}$', date)
    if not valid_format:
        return { 'error': 'Invalid date format!' }
    month = re.findall('[0-9]{2}', date)[0]
    day = re.findall('[0-9]{2}', date)[1]
    year = re.findall('[0-9]{4}', date)[0]
    if int(year) < 1965 or int(year) > 2022:
        return { 'error': 'Date out of range!' }
    return { 'setlist_date': day + '-' + month + '-' + year, 'us_date': month + '-' + day + '-' + year }

def get_show(date: str):
    url = 'https://api.setlist.fm/rest/1.0/search/setlists?artistName=grateful%20dead&date=' + date + 'p=1'
    headers = {'Accept': 'application/json', 'x-api-key': setlist_token}
    response = requests.get(url, headers=headers)
    json_data = json.loads(response.text)
    if not 'setlist' in json_data:
        return { 'error': 'No shows available on this date.'}
    show_loc = json_data['setlist'][0]['venue']['name']
    set_one = json_data['setlist'][0]['sets']['set'][0]['song']
    set_two = json_data['setlist'][0]['sets']['set'][1]['song']
    setlist = []
    for i in set_one:
        setlist.append(i['name'])
    for i in set_two:
        setlist.append(i['name'])
    return { 'venue': show_loc, 'setlist': setlist }

async def send_error(msg, err):
    embd = discord.Embed(title='Command Error!', description=err, color=0xAB0C0C)
    embd.set_thumbnail(url='https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Achtung.svg/628px-Achtung.svg.png')
    await msg.channel.send(embed=embd)
    return

async def send_info(msg, title, desc, fields=None):
    embd = discord.Embed(title=title, description=desc, color=0x3467EB)
    embd.set_thumbnail(url='https://upload.wikimedia.org/wikipedia/en/thumb/3/35/Information_icon.svg/200px-Information_icon.svg.png')
    if fields is not None:
        for x in fields:
            embd.add_field(name=x['name'], value=x['value'], inline=False)
    await msg.channel.send(embed=embd)
    return
    
class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        global prefix
        if message.author.bot == True: # ignore messages from bots
            return
        if message.content.startswith(prefix + ' '): # correct prefix check
            args = message.content.split(' ')
            if len(args) < 2: # argument check
                    await send_error(message, 'Please add a command after the bot prefix!')
                    return

            # --- HELP --- #
            if args[1] == 'help':
                if len(args) > 2: # argument check
                    await send_error(message, 'Too many arguments! Use `{0} help` for help with this bot.'.format(prefix))
                    return
                embd = discord.Embed(title='Jerry Bot Help', description='A full list of commands can be seen below', color=0x3467EB)
                embd.add_field(name='`info`', value='Information about Jerry Bot', inline=False)
                embd.add_field(name='`prefix`', value='View or change the bot prefix.', inline=False)
                embd.add_field(name='`setlist`', value='Get a Grateful Dead setlist', inline=False)
                embd.set_thumbnail(url='https://upload.wikimedia.org/wikipedia/en/thumb/3/35/Information_icon.svg/200px-Information_icon.svg.png')
                await message.channel.send(embed=embd)
                return

            # --- INFO --- #
            elif args[1] == 'info':
                if len(args) > 2: # argument check
                    await send_error(message, 'Too many arguments! Use `{0} help` for help with this bot.'.format(prefix))
                    return
                embd = discord.Embed(title='Jerry Bot Information', description='Created by Thenlie, 2022', color=0x3467EB)
                embd.add_field(name='Language', value='Python', inline=False)
                embd.add_field(name='Repository', value='https://github.com/Thenlie/jerry-bot', inline=False)
                embd.set_thumbnail(url='https://upload.wikimedia.org/wikipedia/en/thumb/3/35/Information_icon.svg/200px-Information_icon.svg.png')    
                await message.channel.send(embed=embd)
                return

            # --- PREFIX --- #
            elif args[1] == 'prefix':
                if len(args) == 2:
                    embd = discord.Embed(title='Jerry Bot Prefix', description='Your server\'s prefix is `{0}`. \n Use `{0} prefix help` for a prefix help.'.format(prefix), color=0x3467EB)
                    await message.channel.send(embed=embd)
                    return
                elif len(args) == 3 and args[2] == 'help':
                    embd = discord.Embed(title='Prefix Help', description='A full list of commands can be seen below', color=0x3467EB)
                    embd.add_field(name='`help`', value='List of prefix commands. `{0} prefix help`'.format(prefix), inline=False)
                    embd.add_field(name='`set`', value='Set a new prefix. `{0} prefix set [new-prexif]`'.format(prefix), inline=False)
                    embd.set_thumbnail(url='https://upload.wikimedia.org/wikipedia/en/thumb/3/35/Information_icon.svg/200px-Information_icon.svg.png')
                    await message.channel.send(embed=embd)
                    return
                elif args[2] == 'set':
                    if len(args) < 5: # argument check
                        prefix = args[3]
                        embd = discord.Embed(title='Prefix update successful!', description='Your server\'s prefix is `{0}`'.format(prefix), color=0x3467EB)
                        await message.channel.send(embed=embd)
                else :
                    await send_error(message, 'Too many arguments! Use `{0} prefix help` for help with this command.'.format(prefix))
                    return
                    
            # --- SETLIST --- #
            elif args[1] == 'setlist':
                if len(args) > 3:
                    await send_error(message, 'Too many arguments! Use `{0} setlist help` for help with this command.'.format(prefix))
                    return
                if args[2] == 'help':
                    embd = discord.Embed(title='Setlist Help', description='A full list of commands can be seen below', color=0x3467EB)
                    embd.add_field(name='`help`', value='List of setlist commands. `{0} setlist help`'.format(prefix), inline=False)
                    embd.add_field(name='`[date]`', value='Get a setlist by date (MM-DD-YYYY). `{0} setlist [date]`'.format(prefix), inline=False)
                    embd.set_thumbnail(url='https://upload.wikimedia.org/wikipedia/en/thumb/3/35/Information_icon.svg/200px-Information_icon.svg.png')
                    await message.channel.send(embed=embd)
                    return
                is_valid = validate_date(args[2])
                if 'error' in is_valid:
                    await send_error(message, is_valid['error'] + ' Use `{0} setlist help` for help with this command.'.format(prefix))
                    return
                else:
                    show = get_show(is_valid['setlist_date'])
                    if 'error' in show:
                        embd = discord.Embed(title='Not Found!', description=show['error'], color=0xAB0C0C)
                        embd.set_thumbnail(url='https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Achtung.svg/628px-Achtung.svg.png')
                        await message.channel.send(embed=embd)
                        return
                    embd = discord.Embed(title=is_valid['us_date'], description=show['venue'], color=0xDEDE4E)
                    print(show)
                    list = ''
                    for i,x in enumerate(show['setlist']):
                        if len(x) > 1:
                            list = list + str(i+1) + '. ' + x + '\n'
                    embd.add_field(name='Setlist', value=list, inline=False)   
                    embd.set_footer(text='Information from Setlist.fm (may be incomplete)')
                    await message.channel.send(embed=embd)
                    return
                return
            

intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(bot_token)