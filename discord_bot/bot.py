import discord
from discord.ext import commands
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime, timedelta
import random
import string

intents = discord.Intents.all()
bot = discord.Bot(command_prefix="!", intents=intents)

uri = "mongodb+srv://snipershot281:bIwDZRrqQryzquUh@nyx.hnjano2.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client['nyx']
api_keys = db['api_keys']

def get_key_by_discord_id(discord_id):
    user_data = api_keys.find_one({"discord_id": discord_id})
    return user_data["nyxkey"] if user_data else None

@bot.slash_command(name="generate_key", description="Generates a new API key")
async def generate_key(ctx):
    await ctx.defer(ephemeral=True)
    key = 'nx-' + ''.join(random.choices(string.ascii_letters + string.digits, k=35))
    if get_key_by_discord_id(str(ctx.author.id)):
        await ctx.respond('You already have an API key.')
    else:
        try:
            newkeydata = {
                "discord_id": str(ctx.author.id),
                "nyxkey": key,
                "requests": 0,
                "reset_time": str(datetime.now().isoformat())
            }
            api_keys.insert_one(newkeydata)
            await ctx.respond(f'{ctx.author.mention}, your API key is: {key}')
        except Exception as e:
            await ctx.respond(f'Error generating key: {str(e)}')

@bot.slash_command(name="regenerate_key", description="Regenerates your API key")
async def regenerate_key(ctx):
    await ctx.defer(ephemeral=True)
    try:
        key = 'nx-' + ''.join(random.choices(string.ascii_letters + string.digits, k=35))
        newkeydata = {
            "discord_id": str(ctx.author.id),
            "nyxkey": key,
            "requests": 0,
            "reset_time": str(datetime.now().isoformat())
        }
        api_keys.replace_one({"discord_id": str(ctx.author.id)}, newkeydata)
        await ctx.respond(f'{ctx.author.mention}, your new API key is: {key}')
    except Exception as e:
        await ctx.respond(f'Error regenerating key: {str(e)}')

@bot.slash_command(name="key", description="Retrieves your API key")
async def key(ctx):
    await ctx.defer(ephemeral=True)
    try:
        key_data = get_key_by_discord_id(str(ctx.author.id))
        if key_data:
            await ctx.respond(f'{ctx.author.mention}, your API key is: {key_data}')
        else:
            await ctx.respond('You do not have an API key. Please generate one using the generate_key command.')
    except Exception as e:
        await ctx.respond(f'Error fetching key: {str(e)}')

@bot.slash_command(name="usage", description="Shows the usage of your API key")
async def usage(ctx):
    await ctx.defer(ephemeral=True)
    try:
        key_data = api_keys.find_one({"discord_id": str(ctx.author.id)})
        if key_data:
            requests = key_data["requests"]
            reset_time = datetime.fromisoformat(key_data["reset_time"])
            if datetime.now() - reset_time > timedelta(days=1):
                requests = 0
                reset_time = datetime.now().isoformat()
                key_data["requests"] = requests
                key_data["reset_time"] = reset_time
                api_keys.replace_one({"discord_id": str(ctx.author.id)}, key_data)
            await ctx.respond(f'{ctx.author.mention}, your API key usage is: {requests}/600')
        else:
            await ctx.respond('You do not have an API key. Please generate one using the generate_key command.')
    except Exception as e:
        await ctx.respond(f'Error fetching usage: {str(e)}')

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Made by NyX AI"))

@bot.event
async def on_member_remove(member):
    api_keys.delete_one({"discord_id": str(member.id)})

bot.run("MTE1ODE3MzUyMjUyMzM0NDkyNw.G4msDr.o4Oh_8HeHc7Hn_X3NN6JB3efYEqAaxypFPRusk")
