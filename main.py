import discord
import re
import os
import requests
import json
from server import keep_alive
from datetime import datetime
from replit import db

bot_token = os.environ['TOKEN']
setlist_token = os.environ['SETLIST_KEY']
# prefix = 'j!'
db['prefix'] = 'j!'

def validate_date(date: str):
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
    print(json_data)
    if not 'setlist' in json_data:
        return { 'error': 'No shows available on this date.'}
    show_loc = json_data['setlist'][0]['venue']['name']
    setlist = []
    for i in json_data['setlist'][0]['sets']['set']:
        for j in i['song']:
            setlist.append(j['name'])
    return { 'venue': show_loc, 'setlist': setlist }

def get_todays_shows(date: str):
    day = re.findall('[0-9]{2}', date)[0]
    month = re.findall('[0-9]{2}', date)[1]
    year = re.findall('[0-9]{4}', date)[0]
    shows = []
    for i in range(1965, int(year)):
        print(month + '-' + day + '-' + str(i))
        show = get_show(day + '-' + month + '-' + str(i))
        if 'error' in show:
            continue
        else:
            shows.append({'venue': show['venue'], 'date': month + '-' + day + '-' + str(i)})
    if len(shows) > 0:
        return shows
    else:
        return 0
    

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
        if message.content.startswith(db['prefix'] + ' '): # correct prefix check
            args = message.content.split(' ')
            if len(args) < 2: # argument check
                    await send_error(message, 'Please add a command after the bot prefix!')
                    return

            # --- HELP --- #
            if args[1] == 'help':
                if len(args) > 2: # argument check
                    await send_error(message, 'Too many arguments! Use `{0} help` for help with this bot.'.format(db['prefix']))
                    return
                fields = [
                    {'name': '`info`', 'value': 'Information about Jerry Bot.'},
                    {'name': '`prefix`', 'value': 'View or change the bot prefix.'},
                    {'name': '`setlist`', 'value': 'Get a Grateful Dead setlist.'}
                ]
                await send_info(message, 'Jerry Bot Help', 'A full list of commands can be seen below', fields)
                return

            # --- INFO --- #
            elif args[1] == 'info':
                if len(args) > 2: # argument check
                    await send_error(message, 'Too many arguments! Use `{0} help` for help with this bot.'.format(db['prefix']))
                    return
                fields = [
                    {'name': 'Language', 'value': 'Python'},
                    {'name': 'Repository', 'value': 'https://github.com/Thenlie/jerry-bot'}
                ]
                await send_info(message, 'Jerry Bot Information', 'Created by Thenlie, 2022', fields)
                return

            # --- PREFIX --- #
            elif args[1] == 'prefix':
                if len(args) == 2:
                    embd = discord.Embed(title='Jerry Bot Prefix', description='Your server\'s prefix is `{0}`. \n Use `{0} prefix help` for a prefix help.'.format(db['prefix']), color=0x3467EB)
                    await message.channel.send(embed=embd)
                    return
                elif len(args) == 3 and args[2] == 'help':
                    fields = [
                        {'name': '`help`', 'value': 'List of prefix commands. `{0} prefix help`'.format(db['prefix'])},
                        {'name': '`set`', 'value': 'Set a new prefix. `{0} prefix set [new-prexif]`'.format(db['prefix'])}
                    ]
                    await send_info(message, 'Prefix Help', 'A full list of commands can be seen below', fields)
                    return
                elif args[2] == 'set':
                    if len(args) < 5: # argument check
                        db['prefix'] = args[3]
                        embd = discord.Embed(title='Prefix update successful!', description='Your server\'s prefix is `{0}`'.format(db['prefix']), color=0x3467EB)
                        await message.channel.send(embed=embd)
                else :
                    await send_error(message, 'Too many arguments! Use `{0} prefix help` for help with this command.'.format(db['prefix']))
                    return
                    
            # --- SETLIST --- #
            elif args[1] == 'setlist':
                if len(args) > 3:
                    await send_error(message, 'Too many arguments! Use `{0} setlist help` for help with this command.'.format(db['prefix']))
                    return
                if args[2] == 'help':
                    fields = [
                        {'name': '`help`', 'value': 'List of setlist commands. `{0} setlist help`'.format(db['prefix'])},
                        {'name': '`[date]`', 'value': 'Get a setlist by date (MM-DD-YYYY). `{0} setlist [date]`'.format(db['prefix'])},
                        {'name': '`[today]`', 'value': 'Get all shows performed on today\'s date. `{0} today`'.format(db['prefix'])},
                    ]
                    await send_info(message, 'Setlist Help', 'A full list of commands can be seen below', fields)
                    return
                elif args[2] == 'today':
                    show = get_todays_shows(datetime.today().strftime('%d-%m-%Y'))
                    if show == 0:
                        embd = discord.Embed(title='No Shows Found Today!', description='No shows were played on this date, or I just couldn\'t find any', color=0xAB0C0C)
                        embd.set_thumbnail(url='https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Achtung.svg/628px-Achtung.svg.png')
                        await message.channel.send(embed=embd)
                    else:
                        embd = discord.Embed(title='Today\'s Shows', description=datetime.today().strftime('%m-%d-%Y'), color=0xDEDE4E)
                        list = ''
                        for i,x in enumerate(show):
                            if len(x) > 1:
                                list = list + x['date'] + ' ' + x['venue'] + '\n'
                        embd.add_field(name='Shows', value=list, inline=False)   
                        embd.set_footer(text='Information from Setlist.fm (may be incomplete)')
                        await message.channel.send(embed=embd)
                        return
                is_valid = validate_date(args[2])
                if 'error' in is_valid:
                    await send_error(message, is_valid['error'] + ' Use `{0} setlist help` for help with this command.'.format(db['prefix']))
                    return
                else:
                    show = get_show(is_valid['setlist_date'])
                    if 'error' in show:
                        embd = discord.Embed(title='Show Not Found!', description=show['error'], color=0xAB0C0C)
                        embd.set_thumbnail(url='https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Achtung.svg/628px-Achtung.svg.png')
                        await message.channel.send(embed=embd)
                        return
                    embd = discord.Embed(title=is_valid['us_date'], description=show['venue'], color=0xDEDE4E)
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
keep_alive()
client.run(bot_token)