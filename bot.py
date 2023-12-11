#pylint:disable=W0401
from time import sleep
import sqlite3
import datetime
import re
from apscheduler.schedulers.background import BackgroundScheduler

from botinit import *
from pyrogram import filters, compose
from pyrogram.types import ChatPermissions
from pyrogram import raw

from database import executa_query, sqlite
from utils import *
from palavrasecreta import *
from lobo import postando_lobo, sorteando_lobo, confere_casa, printerro
from info import *
from agenda import *
import demoji
from dl_videos import *
from rich.traceback import install
install()

import logging
import traceback
from pyrogram.types import InputMediaPhoto

class ErrorLogger:
    def __init__(self):
        self.error_list = []

    def add_error(self, error_msg):
        self.error_list.append(error_msg)
    
    def send_errors(self):
    	if self.error_list:
    		for msg_erro in self.error_list:
    			app.send_message(-1002019305196, msg_erro)
    		self.error_list = []

print("funcionando")

error_logger = ErrorLogger()

class Filtro(logging.Filter):
    def filter(self, record):
        if record.levelno >= logging.ERROR:
            # Apenas mensagens de nível ERROR ou superior passarão pelo filtro
            #erro = f"```python\n{record.msg}\n```"
            traceback_str = traceback.format_exc()
            hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            erro = f"```python\n{hora} - {DONO}\n{traceback_str}\n```"
            error_logger.add_error(erro)
            return True # Retorna False para excluir a mensagem do log
        return False
	
# Configurar o FileHandler
file_handler = logging.FileHandler("logs.txt", "w")
file_handler.addFilter(Filtro())

# Configurar o logger com ambos os handlers
logging.basicConfig(handlers=[file_handler], level=logging.ERROR)

logging.getLogger().setLevel(logging.ERROR)

with app:
	try:
		print(2/0)
	except Exception:
		logging.error("bot iniciado")

@brinabot.on_message(filters.chat(LOBINDIE) & filters.inline_keyboard & filters.user(1903115246))
def save_commans(client, message):
    print("oi")
    for button in message.reply_markup.inline_keyboard:
        if button[1].text == "Todos 👥":
            brinabot.request_callback_answer(LOBINDIE, message.id, button[1].callback_data)

        elif button[1].text == "Salvar ✔️":
        	brinabot.request_callback_answer(LOBINDIE, message.id, button[1].callback_data)
    
@brinabot.on_message(filters.user(AUTORIZADOS) & filters.command("buscaplacar", prefixes=list("/.!")))
def busca_placar(client, message):
	formato = "%Y-%m-%d %H:%M:%S"
	data= datetime.strptime(message.text.replace("/buscaplacar ", ""), formato)
	messages = brinabot.search_messages(-1001572420135, "placar")
	placar = "/rank "
	for messagebusca in messages:
		if messagebusca.date > data:
			placar += messagebusca.text + "\n"
	client.send_message(message.chat.id, placar)


@brinabot.on_message(filters.user(AUTORIZADOS) & filters.command("salvar", prefixes=list("/.!")))
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

@brinabot.on_message(filters.user(AUTORIZADOS) & filters.command("enquete"))
def comando_enquete(client, message):
	cria_enquete(message.text, message.chat.id)

	
@brinabot.on_message(filters.user(AUTORIZADOS) & filters.command("addlobo", prefixes=list("/.!")))
def comando_addlobo(client, message):
	membro, numero, *fixo = message.text.replace(".addlobo ","").split()
	casa = confere_casa(numero)
	fixo = 1 if fixo and fixo[0] == '1' else 0
	try:
		usuario = client.get_chat_member(LOBINDIEFIXO, f"{membro}")
		membronome = dict_membros.get(usuario.user.id, usuario.user.first_name)
		membro_username = "@"+usuario.user.username or ""
		sql = f"INSERT INTO lobo (iduser, nomeuser, numero, casa, username) VALUES ('{usuario.user.id}', '{membronome}', {numero}, '{casa}', '{membro_username}')"
		executa_query(sql, "insert")
		client.send_message(message.chat.id, f"{membronome} adicinado com número {numero}.")
	except KeyError:
		client.send_message(message.chat.id, "Username ou ID inválidos.")
	except Exception as E:
		client.send_message(message.chat.id, "Um erro ocorreu: " + E)

@brinabot.on_message(filters.user(AUTORIZADOS) & filters.command("reload", prefixes=list("/.!")))
def comando_reload(client, message):
	sql = "SELECT iduser FROM membros"
	membros = executa_query(sql, "select")
	print(membros)
	for userid in membros:
		try:
			usuario  = client.get_chat_member(LOBINDIEFIXO, userid[0])
			username = usuario.user.username if usuario.user.username is not None else "Null"
			executa_query(f"UPDATE membros SET username = '@{username}' WHERE iduser = '{userid[0]}'", "update")
			time.sleep(0.2)
		except Exception as E:
			time.sleep(1)
	client.send_message(message.chat.id, "Usernames atualizados.")
	
def tenthings():
	brinabot.add_chat_members(LOBINDIE, "@TenThings_Bot")
	regras10things = brinabot.copy_message(LOBINDIE, IMAGENS, 3)
	brinabot.pin_chat_message(LOBINDIE, regras10things.id)
	brinabot.copy_message(LOBINDIE, IMAGENS, 4)
	agora = datetime.datetime.now(tz)
	meio_dia = agora.replace(hour=12, minute=0, second=0, microsecond=0)
	brinabot.send_message(LOBINDIE, "/score@TenThings_Bot", schedule_date = meio_dia)

@brinabot.on_message((filters.regex("Daily Scores")))
def pontua_tenthings(client, message):
	infodata.atualizar_informacoes()
	if infodata.hora != 12:
		return
	pontuacao = message.text.split("\n")[1:]
	placar = "placar\n\n"
	pontos = 40
	for pontuadores in pontuacao:
		nome = pontuadores.split("-")[0]
		nomecorreto = re.sub(r'[^a-zA-Z\s]', '', nome).strip()
		if nomecorreto:
			placar += f"{nomecorreto} {pontos} "
		else:
			placar += f"{nome[3:]} {pontos} "
		if pontos > 20:
			pontos -= 10
		elif pontos > 5:
			pontos -= 5
	brinabot.send_message(STAFF, placar)
	brinabot.ban_chat_member(LOBINDIE, "@TenThings_Bot")
	brinabot.unban_chat_member(LOBINDIE, "@TenThings_Bot")


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
@brinabot.on_message(filters.user(AUTORIZADOS) & filters.command("saves", prefixes=list("/.!")))
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
	
@brinabot.on_message(filters.user(AUTORIZADOS) & filters.command("p", prefixes=list("/.!")))
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

@brinabot.on_message(filters.user(AUTORIZADOS) & filters.command("sql", prefixes=list("/.!")))
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
	mensagem = message.text.replace("/call", "")
	modulo.call = True
	call(message.chat.id, mensagem = mensagem)


@brinabot.on_message(filters.me & filters.command("soma"))
def comando_soma(client, message):
	placar = message.text.replace("/soma", "")
	aplicadorpontos = soma(placar)
	placar = placar + f"\n\naplicador {aplicadorpontos//10}"
	client.edit_message_text(message.chat.id, message.id, placar)
	

@brinabot.on_message(filters.me & filters.command("encerrar"))
def cancela_call(client, message):
	modulo.call = False


@brinabot.on_message(filters.user(AUTORIZADOS) & filters.command("postalobo"))
def posta_lobo(client, message):
	if message.text.replace("/postalobo", ""):
		postando_lobo(LOBINDIEFIXO)
	else:
		postando_lobo(message.chat.id)
		client.delete_messages(message.chat.id, message.id)
	
@brinabot.on_message(filters.user(AUTORIZADOS) & filters.command("sorteialobo"))
def sorteia_lobo(client, message):
	if message.text.replace("/sorteialobo", ""):
		sorteando_lobo(LOBINDIEFIXO)
	else:
		sorteando_lobo(message.chat.id)
		client.delete_messages(message.chat.id, message.id)
		
@brinabot.on_message(filters.user(AUTORIZADOS) & filters.command("ping"))
def comando_ping(client, message):
	client.send_message(message.chat.id, "Pong!\n<i>version: 12.5</i>")
	
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

#verifica_lobo_postado()


@brinabot.on_message(filters.user(AUTORIZADOS) & filters.command("postapalavra"))
def posta_palavra(client, message):
	if message.text.replace("/postapalavra", ""):
		postando_palavra_secreta(LOBINDIEFIXO)
	else:
		postando_palavra_secreta(message.chat.id)
		client.delete_messages(message.chat.id, message.id)

@brinabot.on_message(filters.bot & filters.regex(r'\b(?:SEGUNDA|TERÇA|QUARTA|QUINTA|SEXTA|SÁBADO|DOMINGO)\b'))
def fixa_saves(client, message):
	infodata.atualizar_informacoes()
	if (infodata.hora == 0 and infodata.minuto < 2):
		brinabot.pin_chat_message(message.chat.id, message.id)
	

@brinabot.on_message(filters.user(AUTORIZADOS) & filters.command("testeps"))
def comando_testeps(client, message):
	palavras = '{"palavra1": "dica1", "palavra2": "dica2", "palavra3": "dica3", "palavra4": "dica4", "palavra5": "dica5"}'
	#palavras = '{"palavra5": "dica5"}'
	infodata.atualizar_informacoes()
	sql = f"INSERT INTO palavra_teste(idmessage, tema, palavras, Data) VALUES ({message.id}, 'palavras', '{palavras}', '{infodata.hoje}')"
	executa_query(sql, "insert")
	ps.force_update()

@brinabot.on_message(filters.user(AUTORIZADOS) & filters.command("validarpalavra"))
def comando_validar_palavra(client, message):
	idmessage = message.text.replace("/validarpalavra","").strip()
	if idmessage:
		message = client.get_messages(LOBINDIE, int(idmessage))
		chute = conferir_chute(message.text, ps.palavras)
		palavra_secreta(message.from_user, chute, message.id, LOBINDIE)
	else:
		chute = conferir_chute(message.reply_to_message.text, ps.palavras)
		palavra_secreta(message.reply_to_message.from_user, chute, message.reply_to_message.id, message.chat.id)


@brinabot.on_message(filters.reply & filters.chat(LOBINDIE) & filters.text)
def envia_lobo(client, message):
	"""
    Função para processar mensagens de resposta relacionadas ao jogo "Lobo".
	"""
	#idmessagelobo, pontos= sqlite.executa("SELECT idmessage, pontos FROM lobo")
	pontos = int(executa_query("SELECT valor FROM valores WHERE nome = 'pontoslobo'", "select")[0][0])
	idmessagelobo = int(executa_query("SELECT valor FROM valores WHERE nome = 'lobomessageid'", "select")[0][0])
	print(idmessagelobo)
	if message.reply_to_message.id == idmessagelobo or message.reply_to_message_id == idmessagelobo:
		sql = f"SELECT * FROM lobo WHERE iduser = {message.from_user.id}"
		membrosalvo = executa_query(sql, "select")
		casa = confere_casa(message.text)
		username = "@"+message.from_user.username if message.from_user.username else " "

		nome_membro = membroslb.dict.get(message.from_user.id, message.from_user.first_name)

		if not membrosalvo:
			print("membrosalvo")
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
		print("else")
		if message.text and len(message.text) < 80 and ps.palavras:
			chute = conferir_chute(message.text, ps.palavras)
			print(chute)
			if chute:
				palavra_secreta(message.from_user, chute, message.id, message.chat.id)


@brinabot.on_message(filters.me & filters.command("reloadlobo"))
def reload_lobo(client, message):
	pass
	
"""def reloaded():
	idmessagelobo = sqlite.executa("SELECT idmessage FROM lobo")
	for message in brinabot.get_discussion_replies(LOBINDIE, idmessagelobo[0]):
		casa = confere_casa(message.text)
		fixo = 0
		try:
			usuarioid = message.from_user.id
			usuarionome = message.from_user.first_name
			username = "@"+message.from_user.username or ""
			membronome = dict_membros.get(usuarioid, usuarionome)
			sql = f"INSERT INTO lobo (iduser, nomeuser, numero, casa, username) VALUES ('{usuarioid}', '{membronome}', {message.text}, '{casa}', '{username}')"
			executa_query(sql, "insert")
		except:
			print("deu erro")"""
		
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

@brinabot.on_message(filters.chat(LOBINDIEFIXO) & filters.regex("🏆 Parabéns aos ganhadores!") & filters.bot)
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


@brinabot.on_message(filters.user(AUTORIZADOS) & filters.command("adicionar"))
def add_bulas(client, message):
	bulas = message.text.replace("/adicionar ","").split("\n")
	for bula in bulas:
		print("oi")
		bula = demoji.replace(bula, "")
		executa_query(f"INSERT INTO bulas(nome) VALUES ('{bula.strip()}')", "insert")
	client.send_message(message.chat.id, "Bulas adicionadas.")


@brinabot.on_message(filters.user(AUTORIZADOS) & filters.command("pesquisar"))
def pesquisa_bulas(client, message):
	bulas = message.text.replace("/pesquisar ","").split(",")
	print(bulas)
	encontradas = ""
	for bula in bulas:
		buscabula = executa_query(f"SELECT nome FROM bulas WHERE nome = '{bula.strip()}'", "select")
		print(buscabula)
		if buscabula:
			print("encontrado")
			encontradas += f"{bula}\n"
	if encontradas:
		client.send_message(message.chat.id, f"As seguintes bulas foram encontradas:\n\n{encontradas}")
	else:
		client.send_message(message.id, f"Nenhuma bula foi encontrada.")
		
		
@brinabot.on_message(filters.user(AUTORIZADOS) & filters.command("eval"))
def comando_eval(client, message):
	comando = message.text.replace("/eval ", "")
	exec(comando)
	
"""@botreserva.on_message(filters.user(AUTORIZADOS) & filters.command("eval"))
def comando_eval_bot(client, message):
	comando = message.text.replace("/eval ", "")
	exec(comando)"""
	

@brinabot.on_message(filters.user(AUTORIZADOS) & filters.command("getlog"))
def get_log(client, message):
	brinabot.send_document(message.chat.id, "erros.txt")
	
@brinabot.on_message(filters.user(AUTORIZADOS) & filters.command("modulos"))
def comando_modulos(client, message):
	comando = message.text.split()
	if len(comando) > 1:
		executa_query(
			f"UPDATE modulos SET {comando[1]} = CASE WHEN {comando[1]} = TRUE THEN FALSE ELSE TRUE END WHERE grupoid = {LOBINDIE}", "update"
		)
		modulo.atualiza_modulos()
		client.send_message(message.chat.id, f"O módulo {comando[1]} foi alternado.")
	else:
		status = executa_query(
			f"SELECT * FROM modulos WHERE grupoid = '{LOBINDIE}'", "select", True
		)[0]
		modulos = f"""palavra_secreta: {status["palavra_secreta"]}
	lobo: {status["lobo"]}
	quiz: {status["quiz"]}
	call: {status["callmembros"]}
	aniver: {status["aniver"]}
	tenthings: {status["tenthings"]}
	""".replace("1", "Ativado")
		client.send_message(message.chat.id, modulos)
"""
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
            
@brinabot.on_message(filters.new_chat_members & filters.chat(LOBINDIE))
def comando_novos_membros(client, message):
	membro = message.new_chat_members[0]
	for idmembro in membroslb.get_membros().keys():
		
		if membro.id == idmembro:
			username = membro.username if membro.username is not False else ""
			if username:
				executa_query(f"UPDATE membros SET username = '@{membro.username}' WHERE iduser = '{idmembro}'", "update")
		else:
			executa_query(f"INSERT INTO membros (username,) VALUES@{membro.username}' WHERE iduser = '{idmembro}'", "update")
			
		
"""	
@brinabot.on_message(filters.poll & filters.chat(int(INDIEMUSIC)))
def comando_poll_indiemusic(client, message):
	link_poll = f"<a href='https://t.me/c/{INDIEMUSIC[4:]}/{message.id}'>CLIQUE AQUI</a>"
	votacao = f"""A VOTAÇÃO para decisão da música da semana já iniciou.

↳ {link_poll} para ter acesso e deixar seu voto 🎶🎶"""
	client.send_message(INDIECANAL, votacao)
	
def grupo_gamee(estado):
	if estado:
		brinabot.set_chat_permissions(
			-1001635100172, 
			ChatPermissions(
        		can_send_messages=True,
        		can_send_media_messages=True,
        		can_send_other_messages=True,
        		can_add_web_page_previews=True,
        		can_send_polls=True
        		)
		)
		
	else:
		brinabot.copy_message(-1001635100172, IMAGENS, 2)
		brinabot.set_chat_permissions(
			-1001635100172, 
			ChatPermissions(
        		can_send_messages=False
        		)
		)

@brinabot.on_message(filters.chat(LOBINDIE))
def handle_all_messages(client, message):
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
   
def posta_indiemusic():
	brinabot.copy_message(INDIECANAL, IMAGENS, 6)

def encerra_indiemusic():
	brinabot.copy_message(INDIECANAL, IMAGENS, 7)

#modulo.postar_lobo()
def gerenciador():
    dia_na_semana = DateTimeInfo().semana
    if dia_na_semana == "Sunday":
    	grupo_gamee(True)
    	brinabot.send_message(LOBINDIE, "/domingo")
    	
    elif dia_na_semana == "Monday":
        modulo.postar_lobo(postando_lobo)
        brinabot.send_message(LOBINDIE, "/segunda")
        
    elif dia_na_semana == "Tuesday":
    	modulo.postar_ps(postando_palavra_secreta)
    	encerra_indiemusic()
    	brinabot.send_message(LOBINDIE, "/terca")
    	
    elif dia_na_semana == "Wednesday":
        modulo.postar_lobo(postando_lobo)
        brinabot.send_message(LOBINDIE, "/quarta")
        
    elif dia_na_semana == "Thursday":
    	modulo.postar_ps(postando_palavra_secreta)
    	brinabot.send_message(LOBINDIE, "/quinta")

    elif dia_na_semana == "Friday":
    	modulo.postar_lobo(postando_lobo)
    	brinabot.send_message(LOBINDIE, "/sexta")
    	
    elif dia_na_semana == "Saturday":
    	modulo.postar_tenthings(tenthings)
    	#brinabot.send_message(LOBINDIE, "/sabado")

	
def sched_erro():
	brinabot.send_message(TESTES, "Tarefa deu erro")
#help(schedule.run_pending())
sched = BackgroundScheduler(daemon=True, timezone=tz)
try: 
	sched.add_job(modulo.postar_lobo,'cron', day_of_week= 'mon, wed, fri', hour = '20', minute = '01', args =[sorteando_lobo])

	sched.add_job(modulo.postar_ps,'cron', day_of_week= 'tue, thu', hour = '16', minute = '00', args = [dicas_ativadas])
	sched.add_job(modulo.postar_ps,'cron', day_of_week= 'tue, thu, sat', hour = '23', minute = '59', args = [palavra_secreta_finalizada])

	sched.add_job(grupo_gamee,'cron', day_of_week= 'sun', hour = '21', minute = '00', args = [False])
	
	sched.add_job(posta_indiemusic, 'cron', day_of_week= 'mon', hour = '08')
	
	sched.add_job(gerenciador,'cron', day_of_week= '0-6', hour = '00', minute = '00')

	sched.add_job(error_logger.send_errors, 'interval', minutes=1)

except Exception as E:
	with brinabot:
		brinabot.send_message(LOGS, E)
		
#sched.add_job(postando_lobo,'interval', minutes = 5)
#sched.add_job(sorteando_lobo,'interval', minutes = 1)
sched.start()
import sys

print("fibalizado")
#brinabot.run()
try:
	compose(apps)
except:
	sys.exit()
	