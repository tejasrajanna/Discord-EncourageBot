import discord
import os  # only needed for env
import requests  # http request to get data from API
import json  # API returns JSON
import random  # to choose encouragements
# from replit import db  # replit database
from keep_alive import keep_alive
from dotenv import load_dotenv
import pymongo

load_dotenv()

myclient = pymongo.MongoClient(os.environ['mtoken'])
mydb = myclient["discordbot"]

client = discord.Client()  # connection to discord

sad_words = ["sad", "depressed", "unhappy", "angry", "miserable", "depressing"]

starter_encouragements = [
    "Cheer up!",
    "Hang in there.",
    "You are a great person!"
]

'''if "responding" not in db.keys():  # switch for encouraging messages
    db["responding"] = True'''

# helper function to return quote from API


def get_quote():
    response = requests.get(
        "https://zenquotes.io/api/random")  # API URL/[mode]
    json_data = json.loads(response.text)  # parsing to json
    quote = json_data[0]['q'] + " -" + \
        json_data[0]['a']  # extracting quote, author
    return(quote)

# helper function to update encouragements


def update_encouragements(encouraging_message):
    try:
        coll = mydb.encouragements
        coll.insert_one({'message': encouraging_message})
    except:
        print("insert attempt failed")

# helper function to delete encouragement


def delete_encouragements(message):
    try:
        coll = mydb.encouragements
        coll.delete_one({'message': message})
    except:
        print('delete failed')


@client.event  # decorator to register an event
# called when bot is ready to be used
async def on_ready():  # asynchronous callback
 # on_... is standard name from library
    print("We have logged in as {0.user}".format(client))
    # 0 is replaced by client and client.user gets username


@client.event
# when bot senses a message in server
async def on_message(message):
    if message.author == client.user:  # if bot user sent the message
        return

    msg = message.content  # extracts the text message

    # responds on specific request to check if bot is online
    if msg.startswith("$hello"):
        await message.channel.send("Hello!")

       # responds on specific request with quote
    if message.content.startswith("$inspire"):
        await message.channel.send(get_quote())

    coll = mydb.encouragements
    temp = list(coll.find())
    messages = []
    for i in temp:
        messages.append(i['message'])

        # responds with encouragement if any sad word is detected
    if any(word in msg for word in sad_words):
        await message.channel.send(random.choice(starter_encouragements))

    # add encouraging message to db
    if msg.startswith("$new"):
        # string.split(seperator,maxsplit) to discard $new
        # extracts required encour.
        encouraging_message = msg.split("$new ", 1)[1]
        update_encouragements(encouraging_message)
        await message.channel.send("New encouraging message added")

    # Delete encouraging message from db
    if msg.startswith("$del"):
        encouragements = []  # returns empty list if encour. not in db
        try:
            # space is optional because we are converting to int
            index = int(msg.split("$del", 1)[1])
            delete_encouragements(index)
            await message.channel.send("deleted encourage message!!")
            #encouragements = db["encouragements"]
        except:
            await message.channel.send("db server down")

    if msg.startswith("$list"):  # to show all encour. messages
        encouragements = []  # if list is empty
        coll = mydb.encouragements
        temp = list(coll.find())
        messages = []
        for i in temp:
            messages.append(i['message'])
        await message.channel.send(messages)
    if msg.startswith('$responding'):  # switch to respond to sad words
        value = msg.split("$responding ", 1)[1]
        try:
            myclient.discordbot()
            await message.channel.send("responding on")
        except:
            await message.channel.send("responding off")

    '''else:
        message.channel.send("wrong message child")'''

keep_alive()  # web server
my_secret = os.getenv('mkey')
client.run(my_secret)
