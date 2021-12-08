import os
from bot import Bot

bot = Bot(prefix='/', lavalinkpass="password", lavalinkport=80)

my_secret = os.environ.get('TOKEN')

bot.connect(my_secret)
