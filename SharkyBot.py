#####KatyushaV2#####
import discord
from discord.ext import commands
import asyncio
import sys
import random
import time
import configparser
import os
import sqlite3

##Variables & objects##
global VERSION
VERSION = '1.1'
botID = "490034484906033155"
steServer = "196090010871660553"
bot = commands.Bot(command_prefix="!")
connection = sqlite3.connect('STE-Data.db')
cur = connection.cursor()

##Global Variables##
global activeGiveaway
activeGiveaway = False

#Debug mode?
global DEBUG
DEBUG = True

#Lists
killResponses = ["%s 'accidentally' fell in a ditch... RIP >:)", "Oh, %s did that food taste strange? Maybe it was.....*poisoned* :wink:", "I didn't mean to shoot %s, I swear the gun was unloaded!", "*stabs %s* heh.... *stabs again*....hehe, stabby stabby >:D", "%s fell into the ocean whilst holding an anvil...well that was stupid.", "%s died from exposure to Staphylococcus Aureus. Wow that was really specific...", "%s was running on a roof in the rain.....huh, I wonder what they were running from....oh well ¯\_(ツ)_/¯"]
userCommands = ["test", "hug", "pat", "roll", "flip", "remind", "kill", "calc", "addquote", "quote","pfp", "info", "version", "changelog", "links", "link"]
operatorCommands = ["say", "purge", "getBot", "update", "addLink", "addquote"]
op_roles = ["265708944675176460"]
scribe_roles = ["490293039382659093", "265708944675176460"]

#Remove default help command
bot.remove_command('help')

#Util funcs
def getTokens():
    config = configparser.ConfigParser()
    if not os.path.isfile("tokens.cfg"):
        print("tokens file missing. ")
        print("Creating one now.")
        config.add_section("Tokens")
        config.set("Tokens", "Bot", "null")
        with open ('tokens.cfg', 'w') as configfile:
            config.write(configfile)
        print("File created.")
        print("Please edit tokens.cfg and then restart.")
        _ = input()
    else:
        config.read('tokens.cfg')
        global botToken
        botToken = config.get('Tokens', 'Bot')
        
def isOp(member):
    for r in member.roles:
        if r.id in op_roles:
            return True
            return
    return False
    
def isScribe(member):
    for r in member.roles:
        if r.id in scribe_roles:
            return True
            return
    return False
    
    
def debug(msg):
    if DEBUG == True:
        print(msg)
    
def create_tables():
    cur.execute('''CREATE TABLE IF NOT EXISTS quoteList
                     (QUOTES TEXT)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS Links
                     (name TEXT, link TEXT)''')
                     
def register_quote(usr, quote):
    quote = usr.name + ': "' + quote + '"'
    cur.execute("INSERT INTO quoteList (quotes) VALUES (?)", (quote,))
    connection.commit()
    
def load_quotes():
    print("Loading Quotes...")
    cur.execute('''SELECT * FROM quoteList''')
    global quotes
    quotes = cur.fetchall()
def get_quote():
    quote = random.choice(quotes)
    quote = str(quote)
    quote = quote.strip("('',)")
    return quote
    
def get_changelog(ver):
    with open ('changelogs/' + ver + '.txt', 'r') as changelog:
        changelog = changelog.read()
        changelog = changelog.splitlines()
    changelog = str(changelog)
    changelog = changelog.replace("',", "\n")
    changelog = changelog.split("['],")
    return changelog
       
def get_link(name):
    cur.execute("SELECT link FROM Links WHERE name = (?)", (name,))
    link = str(cur.fetchall())
    link = link.strip("[(',)]")
    return link
    
def add_link(name, link):
    cur.execute("INSERT INTO Links (name, link) VALUES (?, ?)", (name, link))
    connection.commit()
    print("Link Added")
    
def list_links():
    list = []
    cur.execute('''SELECT name FROM Links''')
    rows = cur.fetchall()
    for row in rows:
        _row = str(row)
        _row = _row.strip("[(',)]")
        list.append(_row)
    print(list)
    return list
    

#Bot Functions
@bot.event
async def on_ready():
    print("Logged in as: " + bot.user.name)
    print("ID: " + bot.user.id)
    print("------------------")
    await bot.change_presence(game=discord.Game(name="Just Keep Swimming"))

#OPERATOR ONLY COMMANDS:
@bot.command(pass_context = True)
async def say(ctx, *, msg: str):
    if isOp(ctx.message.author) == True:
        await bot.delete_message(ctx.message)
        await bot.say(msg)
    else:
        await bot.say("ERROR: UNAUTHORIZED!")

@bot.command(pass_context = True)
async def purge(ctx):
    if isOp(ctx.message.author) == True:
        await bot.say("UNDERSTOOD. I WILL DESTROY THE EVIDENCE!")
        await asyncio.sleep(4)
        async for msg in bot.logs_from(ctx.message.channel):
            await bot.delete_message(msg)
        await bot.say("CHANNEL HAS BEEN PURGED, SIR!")
    else:
        await bot.say("ERROR: UNAUTHORIZED")
        
@bot.command(pass_context = True)
async def getBot(ctx):
    if isOp(ctx.message.author) == True:
        await bot.delete_message(ctx.message)
        await bot.send_message(ctx.message.author, "Invite link:\nhttps://discordapp.com/api/oauth2/authorize?client_id=217108205627637761&scope=bot&permissions=1")
    else:
        await bot.say("ERROR: UNAUTHORIZED!")
        
@bot.command(pass_context = True)
async def update(ctx):
    if isOp(ctx.message.author) == True:
        if ctx.message.channel == bot.get_server(steServer).get_channel(updateChan):
            await bot.delete_message(ctx.message)
            await bot.say("@here I've updated!")
            await bot.say("Changelog for version " + VERSION     + ":")
            for x in get_changelog(VERSION):
                    await bot.say("`" + str(x).strip("['],").replace("'", "") + "`")
        
        else:
            await bot.delete_message(ctx.message)
    else:
        await bot.say("ERROR: UNAUTHORIZED!")
        
@bot.command(pass_context = True)
async def addLink(ctx, name: str=None, *, link: str=None):
    if isScribe(ctx.message.author) == True:
        print("name: " + name)
        print("link: " + link)
        add_link(name, link)
        await bot.delete_message(ctx.message)
        await bot.say("Link Saved!")
    else:
        await bot.say("ERROR: UNAUTHORIZED!")
        
@bot.command(pass_context = True)
async def terminate(ctx):
    if isOp(ctx.message.author) == True:
        await bot.say("Affirmative. Terminating now...")
        await bot.change_presence(status=discord.Status.offline)
        sys.exit()
    else:
        await bot.say("ERROR: UNAUTHORIZED!")
        
@bot.command(pass_context = True)
async def startGiveaway(ctx, *, msg: str=None):
    if isOp(ctx.message.author) == True:
        global activeGiveaway
        if activeGiveaway == True:
            await bot.say("ERROR: There is already a giveaway in progress!")
        else:
            if msg == None:
                await bot.say("ERROR: You cannot start a giveaway with a blank message!")
            else:
                global giveawayEntries
                giveawayEntries = []
                await bot.delete_message(ctx.message)
                await bot.send_message(bot.get_server(vtacServer).get_channel(mainChannel), "@everyone A giveaway is  starting!\n(Remember, you must be a full member to participate in giveaways)\n")
                await asyncio.sleep(5)
                msg = "\n" + msg + "\n\nUse !giveaway to enter the giveaway!"
                em = discord.Embed(title='', description=msg, colour=0xFF0000)
                em.set_author(name='Giveaway Info:', icon_url="https://i.imgur.com/0DCg8JB.png")
                await bot.send_message(bot.get_server(vtacServer).get_channel(mainChannel), embed=em)
                activeGiveaway = True
    else:
        await bot.say("ERROR: UNAUTHORIZED!")
        
@bot.command(pass_context = True)
async def endGiveaway(ctx):
    if isOp(ctx.message.author) == True:
        global activeGiveaway
        activeGiveaway = False
        await bot.send_message(bot.get_server(vtacServer).get_channel(mainChannel), "@everyone The current giveaway is ending! I'm now deciding the winner...")
        await asyncio.sleep(5)
        await bot.send_message(bot.get_server(vtacServer).get_channel(mainChannel), "And the winner is...")
        winner = random.choice(giveawayEntries)
        await bot.send_typing(bot.get_server(vtacServer).get_channel(mainChannel))
        await asyncio.sleep(10)
        await bot.send_message(bot.get_server(vtacServer).get_channel(mainChannel), winner.mention + "! Congratulations! :clap:")    
    else:
        await bot.say("ERROR: UNAUTHORIZED!")
   
        
#USER COMMANDS
@bot.command(pass_context = True)
async def help(ctx):
    usrCmds = '\n'.join("!" + str(c) for c in userCommands)
    em = discord.Embed(title='', description=usrCmds, colour=0xFF0000)
    em.set_author(name='Commands:', icon_url=bot.user.avatar_url)
    await bot.send_message(ctx.message.channel, embed=em)
    #If  user is operator, send dm with op commands
    if isOp(ctx.message.author) == True:
        opCmds = '\n'.join("!" + str(c) for c in operatorCommands)
        em = discord.Embed(title='', description=opCmds, colour=0xFF0000)
        em.set_author(name='High-Command Commands:', icon_url=bot.user.avatar_url)
        await bot.send_message(ctx.message.author, embed=em)

@bot.command()
async def version():
    await bot.say("I am currently on version " + VERSION)
        
@bot.command()
async def test():
    await bot.say("Hello World!")
    
@bot.command(pass_context = True)
async def changelog(ctx, ver: str=VERSION):
    await bot.say("Changelog for version " + ver + ":")
    for x in get_changelog(ver):
        await bot.say("`" + str(x).strip("['],").replace("'", "") + "`")
    
@bot.command(pass_context = True)
async def hug(ctx):
    hug = random.choice([True, False])
    if hug == True:
        await bot.say(ctx.message.author.mention + ": :hugging:")
    else:
        await bot.say(ctx.message.author.mention + ": You don't deserve a hug.")
        
@bot.command()
async def roll(dice : str=None):
    if dice == None:
        await bot.say('Format has to be in NdN!')
        return
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await bot.say('Format has to be in NdN!')
        return

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    await bot.say(result)
      
@bot.command(pass_context = True)
async def flip(ctx):
    await bot.say("Okay, I'll flip it!")
    await bot.send_typing(ctx.message.channel)
    await asyncio.sleep(3)
    if random.choice([True, False]) == True:
        await bot.say(ctx.message.author.mention + ": the result is.......**HEADS**!")
    else:
        await bot.say(ctx.message.author.mention + ": the result is.......**TAILS**!")
      
@bot.group(pass_context = True)
async def remind(ctx, time: str = "0", *, reminder: str="null"):
    time = int(time)
    if time == 0 or reminder == "null":
        await bot.say("Correct Usage: !remind <time in minutes> <reminder>")
        await bot.say("Example: !remind 5 Tell me how reminders work")
        return
    else:
        await bot.delete_message(ctx.message)
        await bot.say("Okay, " + ctx.message.author.mention + "! I'll remind you :smile:")
        await asyncio.sleep(time * 60)
        await bot.send_message(ctx.message.author, "You wanted me to remind you: " + reminder)
        
@bot.command(pass_context = True)
async def kill (ctx, *, member: discord.Member = None):
    if member is None:
        await bot.say(ctx.message.author.mention + ": I need a target!")
        return
    if member.id == ctx.message.author.id:
        await bot.say(ctx.message.author.mention + ": Why do you want me to kill you? :open_mouth:")
    elif member.id == botID:
        await bot.say(ctx.message.author.mention + ": Hah! Don't get cocky kid, I could end you in less than a minute! :dagger:")
    else:
        random.seed(time.time())
        choice = killResponses[random.randrange(len(killResponses))] % member.mention
        await bot.say(choice)
      
@bot.command(pass_context = True)
async def pat(ctx, *, member: discord.Member = None):
    if member is None:
        await bot.say("Aww, does somebody need a headpat? I'll pat you, " + ctx.message.author.mention)
        await bot.send_file(ctx.message.channel, "img/headpat.gif")
    else:
        await bot.say(ctx.message.author.mention + " pats " + member.mention)
        await bot.send_file(ctx.message.channel, "img/headpat.gif")
        
@bot.group(pass_context = True)
async def calc(ctx):
    if ctx.invoked_subcommand is None:
        await bot.say("Invalid arguments! Supported operations are: `add` `subract` `multiply` `divide`")
        await bot.say("Example: `!calc add 1 1` will yield a result of 2")
@calc.command()
async def add(left: float, right: float):
    ans = left + right
    await bot.say(str(left) + " + " + str(right) + " = " + str(ans))
@calc.command()
async def subtract(left: float, right: float):
    ans = left - right
    await bot.say(str(left) + " - " + str(right) + " = " + str(ans))
@calc.command()
async def multiply(left: float, right: float):
    ans = left * right
    await bot.say(str(left) + " * " + str(right) + " = " + str(ans))
@calc.command()
async def divide(left: float, right: float):
    ans = left / right
    await bot.say(str(left) + " / " + str(right) + " = " + str(ans))
    
@bot.command(pass_context = True)
async def addquote(ctx, member: discord.Member = None, *, quote: str=None):
    if isScribe(ctx.message.author) == True:
        if member == None or quote == None:
            await bot.say("You must mention a user and add a quote!")
            await bot.say("Example: `!addquote @Iwan I love quotes`")
        elif member.id == botID:
            await bot.say("ERROR: UNAUTHORIZED! You are not allowed to quote me. Muahahaha!")
            return
        else:
            register_quote(member, quote)
            await bot.delete_message(ctx.message)
            await bot.say("Quote added :thumbsup:")
            load_quotes()
    else:
        await bot.say("ERROR: UNAUTHORIZED!")
       
@bot.command()
async def quote():
    await bot.say(get_quote())
    
@bot.command(pass_context = True)
async def poke(ctx, member: discord.Member=None):
    if member==None:
        await bot.say("I can't poke nobody! Try mentioning someone with `@`, like this\n`!poke @Iwan`")
        return
    else:
        await bot.say(ctx.message.author.mention + " just poked " + member.mention + "!")
        await bot.send_file(ctx.message.channel, "img/poke.gif")
    
@bot.command(pass_context = True)
async def pfp(ctx, member: discord.Member=None):
    if member==None:
        member = ctx.message.author
#        await bot.say("You forgot to give me a user! try mentioning someone with @ next time!")
#        await bot.say("Example: `!pfp @Katyusha`")
#        return
    await bot.say(ctx.message.author.mention + ": Here you go!\n" + member.avatar_url)
        
@bot.command(pass_context = True)
async def info(ctx, member: discord.Member=None):
    if member == None:
        member = ctx.message.author
    info = "Joined server on: " + member.joined_at.strftime("%A %B %d, %Y at %I:%M%p") + "\n"
    info = info + "Account created on: " + member.created_at.strftime("%A %B %d, %Y at %I:%M%p")
    em = discord.Embed(title='', description=info, colour=0xFF0000)
    em.set_author(name=member.name, icon_url=member.avatar_url)
    await bot.send_message(ctx.message.channel, embed=em)

@bot.command(pass_context = True)
async def link(ctx, name: str=None):
    if name == None:
        await bot.say("ERROR: LINK NOT FOUND! \nTry using `!links` to view valid links. \n(Remember, they're case-sensitive)")
    else:
        await bot.say(ctx.message.author.mention + " " + get_link(name))
        
@bot.command(pass_context = True)
async def links(ctx):
    await bot.say(list_links())  


@bot.command(pass_context = True)
async def giveaway(ctx):
    global activeGiveaway
    if activeGiveaway == False:
        await bot.say(ctx.message.author.mention + " There is no active giveaway!")
    else:
        global giveawayEntries
        if ctx.message.author in giveawayEntries:
            await bot.say(ctx.message.author.mention + " You're already entered into the giveaway. No cheating!")
        else:
            _entry = [ctx.message.author]
            giveawayEntries = giveawayEntries + _entry
            await bot.say(ctx.message.author.mention + " has entered into the giveaway!")

    
    
#Runtime, baby! Let's go!    
print ('Getting ready...')
print('Loading SharkBot v' + VERSION)
create_tables()
load_quotes()
getTokens()
bot.run(botToken)
