# inicializacao do bot
from pyrogram import Client
from info import *
import sys




app = Client(
    "wordle-bot",
    api_hash=API_HASH,
    api_id=API_ID,
    bot_token = TOKEN
)
try:
	#brinabot = Client('brinabot', API_ID, API_HASH, session_string=SESSION, phone_number=NUMBER, password="chicobalofo")
except Exception as e:
	with app:
		app.send_message(-1002019305196, f"Erro ao iniciar brinabot: {e}")
		sys.exit()
		
apps = [
        brinabot,
        app
    ]

    #botreserva = Client('bot', API_ID, API_HASH, bot_token="5218571852:AAGfoUCEezSTx0Hs1DisIqZhyOWTzZ8mZrU")
    #apps = [
        #brinabot,
        #botreserva
    #]
"""
with brinabot:
	try:
		chatlogs = brinabot.get_chat("@a2b1d_logsbrinabot")
	except Exception as e:
		chatlogs = brinabot.create_channel("logs brinabot", "canal de logs do userbot.")
		brinabot.set_chat_username(chatlogs.id, "a2b1d_logsbrinabot")
	
	#brinabot.send_message(chatlogs.id, "brinabot iniciado.")
	print(chatlogs.id)
	#brinabot.add_chat_members(chat.id, 5083676810)
"""
import traceback
def teste_exception(e):
	with brinabot:
	    tracetexto = f"local: {e}\n Erro: {e.__traceback__}"
	    print("e:", e)
	    print("type: ", type(e))
	    print("traceback: ", e.__traceback__)
	    #brinabot.send_message(LOGS, tracetexto)
import linecache

def trata_erro(e, *args):
    erro = str(e)
    caminho = e.__traceback__.tb_frame.f_globals['__file__']
    funcao_erro = e.__traceback__.tb_frame.f_code.co_name
    linha_erro = e.__traceback__.tb_lineno
    linha_codigo = linecache.getline(caminho, linha_erro).strip()
    mensagem_erro = f"Erro: {erro}\nCaminho: {caminho}\nFunção que deu erro: {funcao_erro}\nLinha do erro: {linha_erro}\nLinha do código: {linha_codigo}\nArgs: {args}"

    # Enviar mensagem de erro para o canal do Telegram
    brinabot.send_message("@a2b1c_logsbrinabot", mensagem_erro)

"""
    	# Obtenha as informações de rastreamento da exceção
    	tipo_erro = type(e).__name__
    	traceback_info = traceback.format_exc()
    	linha = traceback.tb_lineno(e.__traceback__)
    	arquivo = e.__traceback__.tb_frame.f_code.co_filename
    	funcao = e.__traceback__.tb_frame.f_code.co_name
    	
    	#Crie a mensagem com as informações da exceção
    	mensagem = f'Tipo de erro: {tipo_erro}\nLinha: {linha}\nArquivo: {arquivo}\nFunção: {funcao}\n\n{traceback_info}'

    	brinabot.send_message(LOGS, mensagem)

	
"""
