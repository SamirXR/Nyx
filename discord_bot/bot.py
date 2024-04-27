import discord
from discord.ext import commands
from discord import Embed
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
            await ctx.respond(f'{ctx.author.mention}, your API key usage is: {requests}/1000')
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

@bot.slash_command(name="example-python", description="Shows an example of Python code for OpenAI")
async def example_python(ctx):
    try:
        code = """
# Non Streaming 
```py
from openai import OpenAI

client = OpenAI(api_key="/generate-key", base_url="https://nyx-bqfx.onrender.com/openai")

completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"},
    ],
)

print(completion.choices[0].message.content)```
"""
        await ctx.respond(code)
    except Exception as e:
        await ctx.respond(f'Error fetching code: {str(e)}')


@bot.slash_command(name="example-curl", description="Shows an example of cURL code for OpenAI")
async def example_pythonnnnn(ctx):
    try:
        code = """
# cURL 
```c
curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer YOUR_API_KEY" \
-d '{
  "model": "gpt-3.5-turbo",
  "messages": [
    {"role": "user", "content": "Hey! How Are you?"}
  ]
}' https://nyx-bqfx.onrender.com/openai/chat/completions
```
"""
        await ctx.respond(code)
    except Exception as e:
        await ctx.respond(f'Error fetching code: {str(e)}')

@bot.slash_command(name="example-python-stream", description="Shows an example of Python code for OpenAI Streaming")
async def example_pythonnnn(ctx):
    try:
        code = """
# Streaming       
```py
from openai import OpenAI

client = OpenAI(api_key="/generate-key", base_url="https://nyx-bqfx.onrender.com/openai")

stream = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[{"role": "user", "content": "Hey! How Are you?"}],
  stream=True,
)
for part in stream:
  print(part.choices[0].delta.content or "")```
"""
        await ctx.respond(code)
    except Exception as e:
        await ctx.respond(f'Error fetching code: {str(e)}')

@bot.slash_command(name="example-javascript", description="Shows an example of JavaScript code for OpenAI")
async def example_javascript(ctx):
    try:
        code = """
# JavaScript 
```js
const axios = require('axios');

const apiKey = '/generate-key';
const apiUrl = 'https://nyx-bqfx.onrender.com/openai';
const model = 'gpt-3.5-turbo';

const headers = {
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${apiKey}`
};

const data = {
  model: model,
  messages: [
    { role: 'user', content: 'Hey! How Are you?' }
  ]
};

axios.post(`${apiUrl}/chat/completions`, data, { headers: headers })
  .then(response => {
    const responseDataString = JSON.stringify(response.data, null, 2);
    console.log(responseDataString);
  })
  .catch(error => {
    console.error(`Error: ${error.response.status}, ${error.response.data}`);
  });
```
"""
        await ctx.respond(code)
    except Exception as e:
        await ctx.respond(f'Error fetching code: {str(e)}')

@bot.slash_command(name="api-information", description="Returns the NyX AI's Information")
async def website(ctx):
    nyx_website = "https://nyx-ai.glitch.me"
    base_url = "https://nyx-bqfx.onrender.com/openai"
    discord_invite = "https://discord.gg/rdC7xYvrxu"
    completion_url = "https://nyx-bqfx.onrender.com/openai/chat/completion"
    roleplay_url = "https://nyx-chat.samirawm7.repl.co"
    donation_url = "https://www.buymeacoffee.com/samir.xr"
    github_url = "https://github.com/SamirXR"
    models_url = "https://nyx-bqfx.onrender.com/openai/models"

    embed = discord.Embed(title="NyX AI Information", color=discord.Color.default())

    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1162893971983437976/1173603370498523147/okkkk.png")
    embed.add_field(name="NyX Website", value=nyx_website, inline=False)
    embed.add_field(name="Roleplay URL", value=roleplay_url, inline=False)
    embed.add_field(name="Base URL", value=base_url, inline=False)
    embed.add_field(name="Discord Invite", value=discord_invite, inline=False)
    embed.add_field(name="Completion URL", value=completion_url, inline=False)
    embed.add_field(name="Donation Link", value=donation_url, inline=False)
    embed.add_field(name="GitHub", value=github_url, inline=False)
    embed.add_field(name="Models", value=models_url, inline=False)
    embed.set_footer(text=f"Requested By {ctx.author.name}")  # Adjust size as needed
    await ctx.respond(embed=embed)

@bot.event
async def on_member_leave(member):
    channel = bot.get_channel(913760148302987304)  # replace with your channel ID
    if channel:
        await channel.send(f'{member.name} left the server : |')


@bot.slash_command(name="usage-information", description="Shows the Information about Daily usage")
async def example_pythonnnnnnnnnnnnn(ctx):
    try:
        code = """
# Daily Usage

You get 1000 Credits/Day

Therefore Total Requests Per day 200 (API ) + Unlimited Gemini Bot + Unlimited Roleplay Site
"""
        await ctx.respond(code)
    except Exception as e:
        await ctx.respond(f'Error fetching code: {str(e)}')

@bot.slash_command(name="model-information", description="Shows the Information about NyX Models")
async def example_pythonnnnnnnnnnnnnnn(ctx):
    try:
        code = """
# NyX AI Models

## Chat Models (5/Request)
llama-2-7b
llama-2-13b
llama-2-70b-chat
codellama34-b
claude-instant-1.2
airoboros-70b
mistral-7b
mixtral-8x7B
dolphin-mixtral-8x7b  
lzlv 70b

## GPT Models  (5/Request)
text-search-babbage-doc-001
gpt-4-0613
gpt-4
babbage
gpt-3.5-turbo-0613
text-babbage-001
gpt-3.5-turbo
gpt-3.5-turbo-1106
curie-instruct-beta
gpt-3.5-turbo-0301
gpt-3.5-turbo-16k-0613
text-embedding-ada-002
davinci-similarity
curie-similarity
babbage-search-document
curie-search-document
babbage-code-search-code
ada-code-search-text
text-search-curie-query-001
text-davinci-002
ada
text-ada-001
ada-similarity
code-search-ada-code-001
text-similarity-ada-001
text-davinci-edit-001
code-davinci-edit-001
text-search-curie-doc-001
text-curie-001
curie
davinci
gpt-4-0314


## Premium Models (50/Request)
claude-2.0
claude-2.1
gpt-4
google-gemini-pro

"""
        await ctx.respond(code)
    except Exception as e:
        await ctx.respond(f'Error fetching code: {str(e)}')



bot.run("MTE1ODE3MzUyMjUyMzM0NDkyNw.GRqPJ1.u6JfC_xynhc5ZzlpYg6vAIf-HlBv55zTPJj1Ms")
