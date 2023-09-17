from info import *
from pyrogram import filters
from botinit import get_bot

brinabot = get_bot()

import sqlite3
import demoji
from datetime import datetime, timedelta
from difflib import SequenceMatcher

STAFF =  -1001217627450 # 5083676810

def is_input_accepted(input_string, reference_string):
    max_similarity = 0.9
    similarity_ratio = SequenceMatcher(None, input_string.lower(), reference_string.lower()).ratio()
    if similarity_ratio >= max_similarity:
    	print(reference_string, similarity_ratio)
    return similarity_ratio >= max_similarity
    
@brinabot.on_message(filters.chat(STAFF) & filters.command("addemoji"))
def boss_comando(client, message):
	jogos = message.text.replace("/addemoji", "").replace("/addemoji ", "")
	print(jogos)
	if jogos:
		add_emoji(jogos)

@brinabot.on_message(filters.chat(STAFF) & filters.command("vagenda"))
def comando_formataagenda(client, message):
	agenda = formata_agenda()
	client.send_message(message.chat.id, agenda)
	
@brinabot.on_message(filters.chat(STAFF) & filters.command("vagendac"))
def comando_visualizaagenda(client, message):
	agenda = formata_agenda(True)
	client.send_message(message.chat.id, agenda)
	
@brinabot.on_message(filters.chat(STAFF) & filters.command("vcalendario"))
def comando_formatacalendario(client, message):
	agenda = formata_calendario()
	client.send_message(message.chat.id, agenda)

@brinabot.on_message(filters.chat(STAFF) & filters.command("agenda"))
def comando_salvaagenda(client, message):
	jogos = message.text.replace("/agenda", "")
	if jogos:
		salva_agenda(jogos)
		client.send_message(message.chat.id, "Jogos salvos.")
		
@brinabot.on_message(filters.chat(STAFF) & filters.command("filters"))
def comando_formatafilters(client, message):
	agenda = formata_calendario(True)
	client.send_message(message.chat.id, agenda)

def formata_dias():
	data_atual = datetime.now()	
	# Encontrar o próximo dia da semana (segunda-feira)
	proxima_segunda = data_atual + timedelta((7 - data_atual.weekday()) % 7)	
	# Inicializa uma lista para armazenar os próximos dias
	dias_na_semana = []
	# Adicione a próxima segunda-feira à lista
	dias_na_semana.append(proxima_segunda.strftime("%d/%m"))	
	# Adicione os próximos dias à lista (por exemplo, os próximos 5 dias)
	for i in range(1, 7):  # Este loop adicionará os próximos 5 dias
	    proximo_dia = proxima_segunda + timedelta(days=i)
	    dias_na_semana.append(proximo_dia.strftime("%d/%m"))
	return dias_na_semana

dias_na_semana = formata_dias()


# Conectar ao banco de dados (criará um arquivo de banco de dados chamado 'agenda.db' se não existir)
conn = sqlite3.connect('agenda.db')

# Criar um cursor para executar comandos SQL
cursor = conn.cursor()

@brinabot.on_message(filters.chat(STAFF) & filters.command("dagenda"))
def comando_apagaagenda(client, message):
	conn = sqlite3.connect('agenda.db')
	try:
	
	# Criar um cursor para executar comandos SQL
		cursor = conn.cursor()
		cursor.execute("DELETE FROM agenda WHERE fixo is NULL")
		#cursor.execute("UPDATE jogos SET jogo = LOWER(jogo);")
		conn.commit()
		conn.close()
	except Exception as E:
		print(E)
		
@brinabot.on_message(filters.chat(STAFF) & filters.command("daplicador"))
def comando_removeagenda(client, message):
	conn = sqlite3.connect('agenda.db')
	aplicador = message.text.split()[1]
	if aplicador:
	
	# Criar um cursor para executar comandos SQL
		cursor = conn.cursor()
		cursor.execute(f"DELETE FROM agenda WHERE aplicador ='{aplicador}'")
		#cursor.execute("UPDATE jogos SET jogo = LOWER(jogo);")
		conn.commit()
		conn.close()

	
def verifica_jogo_existente(cursor, game, semana, hora):
    cursor.execute("SELECT COUNT(*) FROM agenda WHERE (semana = ? AND jogo = ?) OR (semana = ? AND hora = ?)", (semana, game, semana, '('+hora+')'))
    count = cursor.fetchone()[0]
    print(count)
    return count > 0
   
def verifica_jogo_vazio(cursor, semana, hora):
    cursor.execute("SELECT COUNT(*) FROM agenda WHERE (semana = ? AND jogo = 'Vazio' AND hora = ?)", (semana, '('+hora+')'))
    count = cursor.fetchone()[0]
    print(count)
    return count > 0
   
   
def salva_agenda(agenda):
	
	conn = sqlite3.connect('agenda.db')
# Criar um cursor para executar comandos SQL
	cursor = conn.cursor()
	
	cursor.execute("SELECT jogo FROM jogos")
	all_jogos = cursor.fetchall()
	
	agenda = agenda.replace("\n\n", "\n")
	jogos_por_aplicador= agenda.split("\n⚡️\n")
	jogos_errados = ""
	for jogos in jogos_por_aplicador:
		jogos = jogos.splitlines()
		aplicador_definido = False
		for jogo in jogos:
			if not aplicador_definido:
				aplicador = jogo.split(" ")[-1][:-1].capitalize()
				aplicador_definido  = True
				jogos_errados += f"\njogos errados do {aplicador}:\n\n"
			else:
				dados_do_jogo = jogo.split(" - ",1)
				dia_semana, hora = dados_do_jogo[0].split(" ")
				if len(dados_do_jogo) > 1:
					nome_do_jogo = demoji.replace(dados_do_jogo[1], "").strip()
					nome_do_jogo = nome_do_jogo[0].upper() + nome_do_jogo[1:].lower()
				else:
					nome_do_jogo = "Vazio"
				
				# Formata nome do dia da semana
				if not dia_semana.lower() in ("sábado, sabado, domingo"):
					dia_semana = dia_semana.lower().replace("terca", "terça")
					dia_semana = dia_semana.upper() + "-FEIRA"
				else:
					dia_semana = dia_semana.upper().replace("SABADO", "SÁBADO")
				
				for nome_correto in all_jogos:
					if is_input_accepted(nome_do_jogo, nome_correto[0]):
						nome_do_jogo = nome_correto[0]
				
				if not verifica_jogo_existente(cursor, nome_do_jogo, dia_semana, hora):
					sql = f"INSERT INTO agenda(aplicador, jogo, semana, hora) VALUES ('{aplicador}', '{nome_do_jogo}', '{dia_semana}', '({hora})')"
					cursor.execute(sql)
					conn.commit()
				elif verifica_jogo_vazio(cursor, dia_semana, hora):
					sql = f"UPDATE agenda SET jogo = '{nome_do_jogo}' WHERE semana = '{dia_semana}' AND hora = '({hora})'"
					cursor.execute(sql)
					conn.commit()
				else:
					jogos_errados += f"{jogo}\n"
	brinabot.send_message(STAFF, jogos_errados)
					
		#aplicador_definido= False
	conn.close()
#salva_agenda(agenda)

def formata_agenda(camps = False):
	conn = sqlite3.connect('agenda.db')

# Criar um cursor para executar comandos SQL
	cursor = conn.cursor()
	agenda = "<b>AGENDA SEMANAL</b> 🗓\n"
	
	dias_da_semana = [
	    "SEGUNDA-FEIRA",
	    "TERÇA-FEIRA",
	    "QUARTA-FEIRA",
	    "QUINTA-FEIRA",
	    "SEXTA-FEIRA",
	    "SÁBADO",
	    "DOMINGO"
	]
	i = 0
	for dia in dias_da_semana:
		sql = f"SELECT * FROM agenda WHERE semana = '{dia}' ORDER BY hora"
		cursor.execute(sql)
		jogos = cursor.fetchall()
		agenda += f"\n<b>{dia} ({dias_na_semana[i]})</b>\n"
		i += 1
		out_agenda = ["Sugestões IndieMusic", "Jogo do lobo", "Palavra secreta", "Votação IndieMusic", "10things [BOT]", "Campeonato de Gamee"]
		for jogo in jogos:
			if jogo[2] in out_agenda:
				pass
			elif "Quiz" in jogo[2]:
				agenda += f"❓ <b>Quiz das {jogo[4][1:-1]} -</b> {jogo[1]}\n"
			elif "Campeonato" in jogo[2]:
				cursor.execute(f"SELECT emoji FROM jogos WHERE jogo='{jogo[2]}'")
				emoji = cursor.fetchone()
				if jogo[2] == "Campeonato de Zumbi":
					emoji = "🧟‍♂"
				elif jogo[2] == "Campeonato de Pega em seis":
					emoji = "🐮"
				if camps:
					agenda += f"{emoji[0]} <b>{jogo[2]} {jogo[4]}</b>\n"
			else:
				agenda += f"🕹 <b>Jogo das {jogo[4][1:-1]} -</b> {jogo[1]}\n"
	conn.close()
	return agenda
		
	# Executar o comando SQL para criar a tabela
#cursor.execute(sql)
#formata_agenda()

#print(cursor.execute("SELECT emoji FROM jogos WHERE jogo='‍Campeonato de Zumbi'").fetchone()[0])


def formata_calendario(saves = False):
	conn = sqlite3.connect('agenda.db')

# Criar um cursor para executar comandos SQL
	cursor = conn.cursor()
	agenda ="" # "<b>CALENDÁRIO SEMANAL</b> 🗓\n"
	
	dias_da_semana = [
	    "SEGUNDA-FEIRA",
	    "TERÇA-FEIRA",
	    "QUARTA-FEIRA",
	    "QUINTA-FEIRA",
	    "SEXTA-FEIRA",
	    "SÁBADO",
	    "DOMINGO"
	]
	i = 0
	for dia in dias_da_semana:
		sql = f"SELECT * FROM agenda WHERE semana = '{dia}' ORDER BY hora"
		cursor.execute(sql)
		jogos = cursor.fetchall()
		agenda += f"\n<b>{dia} ({dias_na_semana[i]})</b>\n"
		i += 1
		for jogo in jogos:
			sql = f"SELECT emoji FROM jogos WHERE jogo='{jogo[2]}'"
			print(sql)
			cursor.execute(sql)
			emoji = cursor.fetchone()
			if emoji:
				emoji = f"{emoji[0]}"
			elif jogo[2] == "Campeonato de Zumbi":
				emoji = "🧟‍♂"
			else:
				emoji = "⚠️"
			agenda += f"{emoji} {jogo[2]} {jogo[4]}\n"
		if saves:
			brinabot.send_message(STAFF,  "/personal " + dia + "\n" + agenda)
			agenda = ""
	print(agenda)
	conn.close()
	return agenda
		
	# Executar o comando SQL para criar a tabela
	cursor.execute(sql)
	
formata_calendario()

def add_emoji(jogos):
	conn = sqlite3.connect('agenda.db')

# Criar um cursor para executar comandos SQL
	cursor = conn.cursor()
	jogos = jogos.splitlines()
	for jogo in jogos:
		emoji = jogo.split()[-1]
		print(emoji)
		nome = demoji.replace(jogo[1:], "").strip()
		print(nome)
		cursor.execute(f"SELECT jogo FROM jogos WHERE jogo='{nome}'")
		resultado = cursor.fetchone()
		print(resultado)
		# Se o jogo não estiver na tabela, insira-o
		if resultado is None:
			print("novo")
			cursor.execute(f"INSERT INTO jogos(emoji, jogo) VALUES ('{emoji}', '{nome}')")
			conn.commit()
	conn.close()
	
def add_emoji1(jogos):
	conn = sqlite3.connect('agenda.db')

# Criar um cursor para executar comandos SQL
	cursor = conn.cursor()
	jogos = jogos.splitlines()
	for jogo in jogos:
		emoji = jogo[0]
		nome = demoji.replace(jogo[:-6], "").strip()
		cursor.execute(f"SELECT jogo FROM jogos WHERE jogo='{nome}'")
		resultado = cursor.fetchone()
		print(resultado)
		# Se o jogo não estiver na tabela, insira-o
		if resultado is None:
			print("novo")
			cursor.execute(f"INSERT INTO jogos(emoji, jogo) VALUES ('{emoji}', '{nome}')")
			conn.commit()
	conn.close()

sql = f"SELECT * FROM jogos"
cursor.execute(sql)
#print(cursor.fetchall())
# Salvar as alterações e fechar a conexão com o banco de dados
conn.commit()
conn.close()
