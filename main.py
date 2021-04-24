import discord
import os #only needed for env
import requests #http request to get data from API
import json #API returns JSON
import random #to choose encouragements
from replit import db #replit database
from keep_alive import keep_alive

client=discord.Client() #connection to discord

sad_words=["sad","depressed","unhappy","angry","miserable","depressing"]

starter_encouragements=[
  "Cheer up!",
  "Hang in there.",
  "You are a great person!"
]

if "responding" not in db.keys(): #switch for encouraging messages
  db["responding"]=True

#helper function to return quote from API
def get_quote():
  response=requests.get("https://zenquotes.io/api/random") #API URL/[mode]
  json_data=json.loads(response.text)  #parsing to json
  quote=json_data[0]['q'] + " -" + json_data[0]['a'] #extracting quote, author
  return(quote)

#helper function to update encouragements
def update_encouragements(encouraging_message):
  if "encouragements" in db.keys(): #returns list of keys in db
    encouragements= db["encouragements"] #extracts encour. from db
    encouragements.append(encouraging_message) #adds new encour.
    db["encouragements"]=encouragements #update db
  else: #if encouragements key not found the create new key
    db["encouragements"]=[encouraging_message]

#helper function to delete encouragement
def delete_encouragements(index):
  encouragements=db["encouragements"]
  if len(encouragements)>index:
    del encouragements[index]
    db["encouragements"]=encouragements
  
@client.event  #decorator to register an event
#called when bot is ready to be used
async def on_ready():  #asynchronous callback
 #on_... is standard name from library
  print("We have logged in as {0.user}".format(client)) 
  #0 is replaced by client and client.user gets username  

@client.event
#when bot senses a message in server
async def on_message(message):  
  if message.author==client.user: #if bot user sent the message
    return;
  
  msg=message.content #extracts the text message

  #responds on specific request to check if bot is online
  if msg.startswith("$hello"): 
    await message.channel.send("Hello!")
  
   #responds on specific request with quote
  if message.content.startswith("$inspire"): 
    await message.channel.send(get_quote())
  
  if db["responding"]: #if switch turned on
    options=starter_encouragements
    if "encouragements" in db.keys():
      #extend adds each element of list as a new element while append adds the whole list as one element , fix ObservedList error
      options.extend(db["encouragements"]) #synchronise with database

    #responds with encouragement if any sad word is detected 
    if any(word in msg for word in sad_words):
      await message.channel.send(random.choice(options))

  #add encouraging message to db
  if msg.startswith("$new"):
    #string.split(seperator,maxsplit) to discard $new
    encouraging_message=msg.split("$new ",1)[1] #extracts required encour.
    update_encouragements(encouraging_message)
    await message.channel.send("New encouraging message added")

  #Delete encouraging message from db
  if msg.startswith("$del"):
    encouragements=[] #returns empty list if encour. not in db
    if "encouragements" in db.keys():
      index=int(msg.split("$del",1)[1]) #space is optional because we are converting to int
      delete_encouragements(index)
      encouragements=db["encouragements"]
    await message.channel.send(encouragements)

  if msg.startswith("$list"): #to show all encour. messages
    encouragements=[] #if list is empty
    if "encouragements" in db.keys():
      encouragements=db["encouragements"]  
    await message.channel.send(encouragements)
  
  if msg.startswith('$responding'): #switch to respond to sad words
    value=msg.split("$responding ",1)[1]
    if value.lower()=="true":
      db["responding"]=True
      await message.channel.send("Responding is on")
    else:
      db["responding"]=False
      await message.channel.send("Responding is off")

keep_alive() #web server
my_secret = os.environ['TOKEN']
client.run(my_secret)
