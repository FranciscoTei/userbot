# inicializacao do bot
from pyrogram import Client
from info import *
import sys

app = Client(
    "app-bot",
    api_hash=API_HASH,
    api_id=API_ID,
    bot_token = TOKEN
)
try:
	brinabot = Client('brinabot', API_ID, API_HASH, session_string=SESSION, phone_number=NUMBER, password="chicobalofo")
except Exception as e:
	with app:
		app.send_message(-1002019305196, f"Erro ao iniciar brinabot: {e}")
		sys.exit()
		
apps = [
        brinabot,
        app
    ]

def trata_erro(e, *args):
	pass