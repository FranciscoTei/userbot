#pylint:disable=W0401
import json
import random
from time import sleep
import sqlite3
import pytz
from apscheduler.schedulers.background import BackgroundScheduler

from botinit import brinabot, trata_erro
from pyrogram import filters
from pyrogram.types import ChatPermissions
from pyrogram import raw
import tgcrypto

from database import executa_query, sqlite
from utils import *
from palavrasecreta import *
from lobo import postando_lobo, sorteando_lobo, confere_casa
from info import *


# Crie um objeto timezone
tz = pytz.timezone('America/Sao_Paulo')

print("iniciado")

def funcaoaqui():
	sql = "SELECT caseiro from lobo WHERE mingau = 'random'"
	executa_query(sql, "select")
	
#funcaoaqui()

@brinabot.on_message(filters.user(AUTORIZADOS) & filters.command("salvar", prefixes=list(".!")))
def salvar_text(client, message):
	try:
		titulo = message.text.removeprefix(".salvar ")
		texto = message.reply_to_message.text
		fixar = int(titulo[-1]) if titulo[-1].isdigit() else 0
		titulo = titulo[:-1] if fixar else titulo
		
		sql = f"INSERT INTO textos (titulo, texto, fixar) VALUES ('{titulo}', '{texto}', {fixar})"
		executa_query(sql, "insert")
		if message.from_user.id == TITULAR:
			client.edit_message_text(message.chat.id, message.id, "<i>Texto salvo com sucesso.</i>")
		else:
			client.send_message(message.chat.id, "<b><i>Texto salvo com sucesso.</i>")
	except Exception as erro:
		 client.send_message(LOGS, erro)

@brinabot.on_message(filters.user(AUTORIZADOS) & filters.command("addlobo", prefixes=list(".!")))
def comando_addlobo(client, message):
	membro, numero, *fixo = message.text.replace(".addlobo ","").split()
	casa = confere_casa(numero)
	fixo = 1 if fixo and fixo[0] == '1' else 0
	try:
		usuario = client.get_chat_member(LOBINDIEFIXO, f"{membro}")
		membronome = dict_membros.get(usuario.user.id, usuario.user.first_name)
		membro_username = usuario.user.username or ""
		sql = f"INSERT INTO lobo (iduser, nomeuser, numero, casa, username) VALUES ('{usuario.user.id}', '{membronome}', {numero}, '{casa}', '{membro_username}')"
		executa_query(sql, "insert")
		client.send_message(message.chat.id, f"{membronome} adicinado com número {numero}.")
	except KeyError:
		client.send_message(message.chat.id, "Username ou ID inválidos.")
	except Exception as E:
		client.send_message(message.chat.id, "Um erro ocorreu: " + E)

@brinabot.on_message(filters.user(AUTORIZADOS) & filters.command("reload", prefixes=list(".!")))
def comando_reload(client, message):
	sql = "SELECT iduser FROM membros"
	membros = executa_query(sql, "select")
	print(membros)
	for userid in membros:
		try:
			usuario  = client.get_chat_member(LOBINDIEFIXO, userid[0])
			username = usuario.user.username if usuario.user.username is not None else " "
			executa_query(f"UPDATE membros SET username = '{username}' WHERE iduser = '{userid[0]}'", "update")
			time.sleep(1)
		except Exception as E:
			time.sleep(1)
	client.send_message(message.chat.id, "Usernames atualizados.")
	
"""with brinabot:
	brinabot.add_chat_members(erros, "@TenThings_Bot")
	regras10things = brinabot.copy_message(erros, -1001217627450, 5329)
	brinabot.pin_chat_message(erros, regras10things.id)
	brinabot.copy_message(erros, -1001217627450, 5330) 
	brinabot.send_message(erros, "/score@TenThings_Bot") """

@brinabot.on_message(filters.user(612900440) & (filters.regex("Daily Scores")))
def pontua_tentings(client, message):
	pontuacao = message.text.split("\n")[1:]
	placar = ""
	for pontuadores in pontuacao:
		nomeplacar = pontuadores.split()[1]
		placar += f"{nomeplacar} 50 "
	#brinabot.send_message(erros, placar)

"""
@brinabot.on_message(filters.chat(staff) & (filters.regex("placar") | filters.regex("Placar")))
def pega_placar(client, message):
	texto = message.text.lower()
	print(texto)
	if texto.startswith("placar"):
		print("oi")
		placar = message.text.split("\n")[1:]
		placar = "\n".join(placar)
		sql = "SELECT texto FROM textos WHERE titulo = 'rankingplacar'"
		placartotal = executa_query(sql,"select")[0][0]
		print(placartotal)
		placartotal += f"{placar}\n"
		client.edit_message_text(ranking, 654587, placartotal)
		sql = f"UPDATE textos SET texto = '{placartotal}' WHERE titulo = 'rankingplacar'"
		executa_query(sql, "update")
"""
@brinabot.on_message(filters.user(AUTORIZADOS) & filters.command("saves", prefixes=list(".!")))
def comando_saves(client, message):
	try:
		sql = "SELECT titulo FROM textos"
		saves = executa_query(sql, "select")
		lista = ""
		for save in saves:
			lista = f"{lista}{save[0]}\n"
		client.edit_message_text(message.chat.id, message.id, lista)
	except Exception as erro:
		 client.edit_message_text(message.chat.id, message.id, erro)
	
@brinabot.on_message(filters.user(AUTORIZADOS) & filters.command("p", prefixes=list(".!")))
def recupera_texto(client, message):
	try:
		comando = message.text.split()
		sql = f"SELECT texto, fixar FROM textos WHERE titulo = '{comando[1]}'"
		texto = executa_query(sql, "select")[0]
		client.edit_message_text(message.chat.id, message.id, texto[0])
		if texto[1] == 1:
			client.pin_chat_message(message.chat.id, message.id)
	except Exception as erro:
		 client.edit_message_text(message.chat.id, message.id, erro)

@brinabot.on_message(filters.user(AUTORIZADOS) & filters.command("sql", prefixes=list(".!")))
def comando_sql(client, message):
	sql = message.text.replace(".sql ", "")
	try:
		if "select" in sql.lower():
		 	resultados = executa_query(sql, "select")
		 	lista = ""
		 	for resultado in resultados:
		 		lista += f"{resultado}\n"
		 	if message.from_user.id == 886429586:
		 		client.edit_message_text(message.chat.id, message.id, f"{lista}\n\n<code>{sql}</code>")
		 	else:
		 		message.reply(f"{lista}\n\n<code>{sql}</code>")
		else:
		 	executa_query(sql, "delete")
		 	if message.from_user.id == 886429586:
		 		client.edit_message_text(message.chat.id, message.id, f"Comando executado com sucesso.\n\n<code>{sql}</code>")
		 	else:
		 		message.reply(f"Comando executado com sucesso.\n\n<code>{sql}</code>")
		 		
	except Exception as e:
         trata_erro(e, sql)


		
@brinabot.on_message(filters.me & filters.command("call"))
def call_jogo(client, message):
	mensagem = message.text.replace("/call ", "")
	call(message.chat.id, mensagem = mensagem)
	
@brinabot.on_message(filters.me & filters.command("cancelar"))
def cancela_call(client, message):
	call(client,message.chat.id, chamar = False)
		
@brinabot.on_message(filters.user(AUTORIZADOS) & filters.command("postalobo"))
def posta_lobo(client, message):
	postando_lobo(message.chat.id)
	client.delete_messages(message.chat.id, message.id)
	
@brinabot.on_message(filters.user(AUTORIZADOS) & filters.command("sorteialobo"))
def sorteia_lobo(client, message):
	sorteando_lobo(message.chat.id)
	client.delete_messages(message.chat.id, message.id)
	
@brinabot.on_message(filters.user(AUTORIZADOS) & filters.command("sqlite", prefixes=list(".!")))
def comando_sqlite(client, message):
	comando = message.text.replace(".sqlite ", "")
	try:
		conn = sqlite3.connect("lobo_postado.db")
		cursorr = conn.cursor()
		cursorr.execute(comando)
		if "select" in comando.lower():
			resultados = cursorr.fetchall()
			lista = ""
			for resultado in resultados:
				lista += f"{resultado}\n"
			if message.from_user.id == 886429586:
				client.edit_message_text(message.chat.id, message.id, f"{lista}\n\n<code>{comando}</code>")
			else:
				message.reply(f"{lista}\n\n<code>{comando}</code>")
		else:
		 	conn.commit()	 	
		 	if message.from_user.id == 886429586:
		 		client.edit_message_text(message.chat.id, message.id, f"Comando executado com sucesso.\n\n<code>{comando}</code>")
		 	else:
		 		message.reply("Comando executado com sucesso.\n\n<code>{comando}</code>")

		conn.close()
	except Exception as e:
		 client.edit_message_text(message.chat.id, message.id, e)
						
@brinabot.on_message(filters.chat(LOBINDIE) & filters.regex("Esperamos que você se sinta confortável conosco") & filters.bot)
def deleta_mcombot(client, message):
	client.delete_messages(message.chat.id, message.id)


def verifica_lobo_postado():
	# obtém o nome do dia da semana correspondente ao número
	if infodata.semana in ('Monday', 'Wednesday', 'Friday') and infodata.hora < 1:
		conn = sqlite3.connect("lobo_postado.db")
		cursorr = conn.cursor()
		comando = "SELECT data FROM lobo WHERE IR = 1"
		cursorr.execute(comando)
		dialobo = cursorr.fetchone()[0]
		if infodata.hoje == dialobo:
			print("lobo foi postado")
		else:
			with brinabot:
				postando_lobo(LOBINDIE)

verifica_lobo_postado()

def search_date():
	try:
		mensagens = brinabot.get_chat_history(1945928748, limit = 15)
		salvar = ""
		for messages in mensagens:
			if messages.text:
				salvar+= messages.text
		sql = f"INSERT INTO palavra_postada (tema, palavras) VALUES ('tema', '{salvar}')"
		executa_query(sql, "insert")
	except:
		pass

@brinabot.on_message(filters.user(AUTORIZADOS) & filters.command("postapalavra"))
def posta_palavra(client, message):
	ps.palavras = postando_palavra_secreta(message.chat.id)
	client.delete_messages(message.chat.id, message.id)

@brinabot.on_message(filters.reply & filters.chat(LOBINDIE))
def envia_lobo(client, message):
	"""
    Função para processar mensagens de resposta relacionadas ao jogo "Lobo".
	"""
	idmessagelobo, pontos= sqlite.executa("SELECT idmessage, pontos FROM lobo")
	print(idmessagelobo)
	
	if message.reply_to_message.id == idmessagelobo:		
		sql = f"SELECT * FROM lobo WHERE iduser = {message.from_user.id}"
		membrosalvo = executa_query(sql, "select")
		casa = confere_casa(message.text)
		username = "@"+message.from_user.username if message.from_user.username else " "

		nome_membro = membroslb.dict.get(message.from_user.id, message.from_user.first_name)
		if not membrosalvo:
			executa_query(
				f"INSERT INTO lobo (iduser, nomeuser, numero, casa, username) VALUES ('{message.from_user.id}', '{nome_membro}', {message.text}, '{casa}', '{username}')",
				"insert"
			)
		else:
			executa_query(
				f"UPDATE lobo SET numero = {message.text}, casa = '{casa}', username = '{username}' WHERE iduser = '{message.from_user.id}'",
				 "update"
			)
			
		postando_lobo(message.chat.id, idmessagelobo)
	
	# Conferindo se o usuário chutou uma palavra secreta
	else:
		if message.text and len(message.text) < 80:
			chute = conferir_chute(message.text, ps.palavras)
			if chute:
				palavra_secreta(message.from_user, chute, message.id, message.chat.id)

@brinabot.on_message(filters.reply & filters.chat(LOBINDIE))
def atualiza_palavra(client, message):
	if message.text and len(message.text) < 80:
		palavra_secreta(message.from_user, message.text, message.id, message.chat.id)
	

@brinabot.on_message(filters.chat(LOBINDIE) & filters.regex("🎲 O quiz está prestes a começar...") & filters.bot)
def muta_grupo(client, message):
	client.set_chat_permissions(message.chat.id, ChatPermissions(can_send_messages=False))
	chat_reactions = raw.types.ChatReactionsNone()
	brinabot.invoke(raw.functions.messages.SetChatAvailableReactions(peer = brinabot.resolve_peer(LOBINDIE), available_reactions = chat_reactions))
	messageid = message.reply("<b>⚠ | O grupo será mutado em segundos.</b>")
	dots = [".", ".."]
	for dot in dots:
		sleep(1)
		client.edit_message_text(message.chat.id, messageid.id, f"<b>⚠ | O grupo será mutado em segundos.{dot}</b>")
	client.edit_message_text(message.chat.id, messageid.id, "<b>O grupo está mutado</b> 🔇")

@brinabot.on_message(filters.chat(LOBINDIE) & filters.regex("🏆 Parabéns aos ganhadores!") & filters.bot)
def libera_grupo(client, message):
	try:
		client.set_chat_permissions(message.chat.id, ChatPermissions(can_send_messages = True, can_send_media_messages=True, can_send_other_messages=True, can_send_polls= True, can_add_web_page_previews= True, can_invite_users= True))
		chat_reactions = raw.types.ChatReactionsAll()
		brinabot.invoke(raw.functions.messages.SetChatAvailableReactions(peer = brinabot.resolve_peer(LOBINDIE), available_reactions = chat_reactions))
		message.reply("<b>Grupo liberado para falar novamente.</b>")
	except Exception as e:
		client.send_message(LOGS, e)
	finally:
		placar = placar_quiz(message.text, client)
		client.send_message(message.chat.id, placar)

@brinabot.on_message(filters.user(AUTORIZADOS) & filters.command("quiz"))
def envia_placar(client, message):
	placar = message.text.replace("/quiz ", "")
	#transforna um quiz em placar
	placar = placar_quiz(placar, client)
	client.send_message(message.chat.id, placar)
	placarstaff = "placar\n\n" + placar.replace("\n", " ")
	client.send_message(STAFF, placarstaff)

@brinabot.on_message(filters.command("helpsql"))
def comando_helsql(client, message):
	mensagem = """
🔎 <b>SELECT:</b> <i>Usado para recuperar dados de uma tabela.</i>

<code>SELECT coluna1, coluna2 ... FROM tabela WHERE coluna = valor</code>

obs¹: é possível usar &quot;*&quot; no lugar de colunas para selecionar todas as colunas
➖➖➖➖➖➖➖➖➖➖
➕ <b>INSERT:</b> <i>Usado para adicionar novos registros a uma tabela.</i>

INSERT INTO nome<i>tabela (coluna1, coluna2) VALUES (valor1, valor2);
➖➖➖➖➖➖➖➖➖➖
🔄 <b>UPDATE:</b> <i>Usado para modificar registros existentes em uma tabela.</i>

UPDATE nome</i>tabela SET coluna1 = novo<i>valor WHERE coluna = valor

Obs¹: se não especificar uma condição (WHERE) todos as linhas da tabela serão atualizadas com esses valores
➖➖➖➖➖➖➖➖➖➖
❌ <b>DELETE:</b> <i>Utilizado para remover registros de uma tabela.</i>

DELETE FROM nome</i>tabela WHERE coluna = valor

Obs¹: Se não especificar uma condição (WHERE) todos os dados da tabela serão apagados
"""
	client.send_message(message.chat.id, mensagem)
	
@brinabot.on_message(filters.user(AUTORIZADOS) & filters.command("verpalavras"))
def ver_palavras(client, message):
	if ps.palavras:
		palavras = "Palavras: "
		for palavra in ps.palavras.keys():
			palavras += f"<code>{palavra}</code> - "
		#texto = f"Palavras: {' - '.join([<code>valor<\code> for valor in palavras_secretas.keys()])}"
	else:
		palavras= "Nao há palavras."
	client.send_message(message.chat.id, palavras)
	try:
		search_date()
	except:
		pass
	
# Defina o filtro para capturar o evento ChatMemberUpdated
@brinabot.on_chat_member_updated(filters.chat(LOBINDIE))
def handle_chat_member_updated(client, update):
    # Verifique se o usuário foi adicionado ao grupo
    if update.new_chat_member:
        # Obtenha o objeto ChatMember do usuário recém-adicionado
        new_member = update.new_chat_member
        print(new_member)
        # Verifique se o usuário tem um username
        if new_member.user.username:
            username = new_member.user.username
            print(f"Novo membro com username: @{username}")
        else:
            print("Novo membro sem username")


ids = ()
@brinabot.on_message(filters.chat(LOBINDIE))
def handle_all_messages(client, message):
	global ids
	#quant = message.text.replace(" ","")
	#quant = len(quant)
	"""listapalavras = message.text.split("\n\n")

	placar = ""
	for chute in listapalavras:
	   nome, quant = chute.split(":\n")
	   quant = len(quant.replace(" ", ""))
	   placar += f"{nome}: {quant}\n"
    
	brinabot.send_message(message.chat.id, placar, reply_to_message_id=message.id)"""
	if ps.palavras:
		if message.text and len(message.text) < 80:
			chute = conferir_chute(message.text, ps.palavras)
			if chute:
				palavra_secreta(message.from_user, chute, message.id, message.chat.id)

#help(schedule.run_pending())
sched = BackgroundScheduler(daemon=True, timezone=tz)
try: 
	sched.add_job(postando_lobo,'cron',day_of_week= 'mon, wed, fri', hour = '00', minute = '01')
	sched.add_job(sorteando_lobo,'cron', day_of_week= 'mon, wed, fri', hour = '20', minute = '00')
	
	sched.add_job(postando_palavra_secreta,'cron', day_of_week= 'tue, thu, sat', hour = '00', minute = '01')
	sched.add_job(dicas_ativadas,'cron', day_of_week= 'tue, thu,sat', hour = '16', minute = '28')
	sched.add_job(palavra_secreta_finalizada,'cron', day_of_week= 'tue, thu, sat', hour = '23', minute = '59')
except Exception as E:
	with brinabot:
		brinabot.send_message(LOGS, E)

#sched.add_job(postando_lobo,'interval', minutes = 5)
#sched.add_job(sorteando_lobo,'interval', minutes = 1)
sched.start()
print("fibalizado")
brinabot.run()
