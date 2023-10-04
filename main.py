import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import random
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId

load_dotenv()

admins = [384449598305075200]

passw = os.getenv('PASSWORD')

uri = f"mongodb+srv://purci:{passw}@cluster0.ertx51f.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri, server_api=ServerApi('1'))
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
    
db = client["Slotbot"]
playerdata = db["Player Data"]

intents = discord.Intents.all()
bot = discord.Bot(intents=intents)

async def getplayer(id):
    data = playerdata.find_one({"playerid": id})
    return data

async def updateplayer(id, option, value):
    data = playerdata.find_one({"playerid": id})
    
    if data:
        query = {"_id": data['_id']}
        if option == "wallet":
            update = {"$set": {"wallet": value}}
        elif option == "bank":
            update = {"$set": {"bank": value}}
        
        result = playerdata.update_one(query, update, upsert=False)
    
async def createplayer(id):
    data = {
        "playerid": id,
        "wallet": 0,
        "bank": 0
    }
    playerdata.insert_one(data)

async def checkplayer(id):
    data = await getplayer(id)
    exists = False
    if not str(data) == 'None':
        exists = True
        return exists
    else:
        await createplayer(id)
        return exists


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    
@bot.event
async def on_message(msg):
    if bot.user.mention in msg.content:
        embed = discord.Embed(title="Hi, I'm Slotbot!",description="I use slash commands!")
        await msg.channel.send(embed=embed)
        
@bot.slash_command(description="Check your balance")
async def balance(ctx):
    exists = await checkplayer(ctx.author.id)
    if exists == True:
        data = await getplayer(ctx.author.id)
        embed=discord.Embed(title="Your Balance")
        embed.add_field(name="Wallet", value=data['wallet'], inline=True)
        embed.add_field(name="Bank", value=data['bank'], inline=True)
        await ctx.respond(embed=embed)
    else:
        await ctx.respond("No player was found, new player has been created.")
        
        
@bot.slash_command(description="Beg for money on the streets like a homeless person.")
async def beg(ctx):
    exists = await checkplayer(id)
    response = {
        "A Nice Business Man Gives you some money": random.randint(50, 100),
        "A Rich Retired Old Man Gives you some money": random.randint(200, 500),
        "A Kind Stranger Offers You Help": random.randint(100, 300),
        "Someone Pities You and Gives You a Few Coins": random.randint(20, 50),
        "A Generous Samaritan Donates to Your Cause": random.randint(150, 300),
        "You Receive Spare Change from a Passerby": random.randint(10, 30),
        "A Grumpy Person Gives You a Small Amount of Money": random.randint(5, 20),
        "A Compassionate Woman Offers You Support": random.randint(50, 120),
        "A Group of Friends Pitch In to Help You Out": random.randint(80, 180),
        "A Shopkeeper Shows Some Sympathy and Contributes": random.randint(30, 70),
        "A Teenager Offers You Their Saved Pocket Money": random.randint(15, 40),
        "A Gentleman Shares a Portion of His Wealth": random.randint(100, 250),
        "A Helpful Bystander Gives You a Boost": random.randint(40, 90),
        "A Local Community Member Lends a Hand": random.randint(60, 150),
        "A Supportive Tourist Gives You a Donation": random.randint(25, 60),
        "A Fellow Beggar Shares Their Meager Earnings": random.randint(5, 15),
        "A Family Passes On Their Spare Change to You": random.randint(10, 25),
        "A Charity Worker Provides Assistance": random.randint(70, 160),
        "A Sympathetic Neighbor Offers You Help": random.randint(35, 80),
        "A Kind-hearted Child Donates Their Piggy Bank Savings": random.randint(5, 30),
    }
    begresp, money = random.choice(list(response.items()))
    embed = discord.Embed(title=begresp,description=f"You earned ${money}")
    await ctx.respond(embed=embed)
    data = await getplayer(ctx.author.id)
    newbal = data['wallet'] + money
    await updateplayer(ctx.author.id, "wallet", newbal)
    
@bot.slash_command(description="Despoit Money into the bank")
async def deposit(ctx, amount=discord.Option(discord.SlashCommandOptionType.integer, required=False)):
    if amount:
        data = await getplayer(ctx.author.id)
        num = int(amount)
        wallet = int(data['wallet'])
        if num < wallet:
            newbank = int(data['bank']) + num
            newallet = wallet - num
            await updateplayer(ctx.author.id, "bank", newbank)
            await updateplayer(ctx.author.id, "wallet", newallet)
            await ctx.respond(f'${amount} transfered to your bank.')
        else:
            await ctx.respond(f"You don't have ${amount} currently in your wallet.")
    else:
        data = await getplayer(ctx.author.id)
        await updateplayer(ctx.author.id, "bank", data['wallet'])
        await updateplayer(ctx.author.id, "wallet", 0)
        await ctx.respond(f"${data['wallet']} transfered to your bank.")
        
@bot.slash_command(description="Withdraw Money from the bank")
async def withdraw(ctx, amount=discord.Option(discord.SlashCommandOptionType.integer, required=False)):
    if amount:
        data = await getplayer(ctx.author.id)
        num = int(amount)
        bank = int(data['bank'])
        if num < bank:
            newbank = bank - amount
            newallet = int(data['wallet']) + amount
            await updateplayer(ctx.author.id, "bank", newbank)
            await updateplayer(ctx.author.id, "wallet", newallet)
            await ctx.respond(f'${amount} transfered to your wallet.')
        else:
            await ctx.respond(f"You don't have ${amount} currently in your bank.")
    else:
        data = await getplayer(ctx.author.id)
        await updateplayer(ctx.author.id, "bank", 0)
        await updateplayer(ctx.author.id, "wallet", data['bank'])
        await ctx.respond(f"${data['bank']} transfered to your wallet.")
            
            
    
@bot.slash_command()
async def addmoney(ctx, amount: discord.Option(discord.SlashCommandOptionType.integer), user: discord.Option(discord.SlashCommandOptionType.user, required=False)):
    if ctx.author.id in admins:
        if user:
            exists = await checkplayer(user.id)
            data = await getplayer(user.id)
            newbal = data['wallet'] + amount
            await updateplayer(user.id, "wallet", newbal)
            await ctx.respond(f"{user.mention} has been given ${amount}")
        else:
            exists = await checkplayer(ctx.author.id)
            data = await getplayer(ctx.author.id)
            newbal = data['wallet'] + amount
            await updateplayer(ctx.author.id, "wallet", newbal)
            await ctx.respond(f"You have been given ${amount}")
    else:
        await ctx.respond("You don't have the required perms to do that.")
        
@bot.slash_command()
async def delmoney(ctx, amount: discord.Option(discord.SlashCommandOptionType.integer), user: discord.Option(discord.SlashCommandOptionType.user, required=False)):
    if ctx.author.id in admins:
        if user:
            exists = await checkplayer(user.id)
            data = await getplayer(user.id)
            newbal = data['wallet'] + amount
            await updateplayer(user.id, "wallet", newbal)
            await ctx.respond(f"{user.mention} has been given ${amount}")
        else:
            exists = await checkplayer(ctx.author.id)
            data = await getplayer(ctx.author.id)
            newbal = data['wallet'] + amount
            await updateplayer(ctx.author.id, "wallet", newbal)
            await ctx.respond(f"You have been given ${amount}")
    else:
        await ctx.respond("You don't have the required perms to do that.")

token = os.getenv('TOKEN')
bot.run(token)