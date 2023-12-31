from info import *
from pyrogram import filters
from botinit import brinabot
from database import executa_query

import sqlite3
import demoji
from datetime import datetime, timedelta
from difflib import SequenceMatcher


def is_input_accepted(input_string, reference_string):
    if len(input_string) < 10:
    	max_similarity = 0.80
    else:
    	max_similarity = 0.85
    similarity_ratio = SequenceMatcher(None, input_string.lower(), reference_string.lower()).ratio()
    if similarity_ratio >= max_similarity:
    	print(reference_string, similarity_ratio)
    return similarity_ratio >= max_similarity
    
@brinabot.on_message(filters.chat([STAFF, TESTES]) & filters.command("addemoji"))
def comando_addemoji(client, message):
	jogos = message.text.replace("/addemoji", "").replace("/addemoji ", "")
	print(jogos)
	if jogos:
		add_emoji(jogos)
		client.send_message(message.chat.id, "Emojis adicionados.")

@brinabot.on_message(filters.chat([STAFF, TESTES]) & filters.command("vagenda"))
def comando_formataagenda(client, message):
	agenda = "/personal agenda\n\n" + formata_agenda()
	#agenda = agenda.replace("<b>SEXTA-FEIRA (06/10)</b>" , "<b>SEXTA-FEIRA (06/10)</b> - DIA TEMÁTICO DA DISNEY")
	if message.chat.id == STAFF:
		client.edit_message_text(message.chat.id, idmessageagenda, agenda)
		client.send_message(message.chat.id, "Agenda atualizada", reply_to_message_id = idmessageagenda)
	else:
		client.send_message(message.chat.id, agenda)

idmessageagenda = int(executa_query("SELECT valor FROM valores WHERE id = 2", "select")[0][0])

@brinabot.on_message(filters.chat([STAFF, TESTES]) & filters.command("resetagenda"))
def comando_visualizaagenda(client, message):
	idmessageagenda = 0
	executa_query(f"UPDATE valores SET valor = {idmessageagenda} WHERE id = 2", "update")
	
@brinabot.on_message(filters.chat([STAFF, TESTES]) & filters.command("vagendac"))
def comando_visualizaagendacomcampeonato(client, message):
	global idmessageagenda

	agenda = formata_agenda(True)
	#agenda = agenda.replace("<b>SEXTA-FEIRA (06/10)</b>" , "<b>SEXTA-FEIRA (06/10)</b> - DIA TEMÁTICO DA DISNEY")
	if message.chat.id == STAFF and idmessageagenda:
		client.edit_message_text(message.chat.id, idmessageagenda, agenda)
		client.send_message(message.chat.id, "Agenda atualizada", reply_to_message_id = idmessageagenda)
	elif message.chat.id == STAFF:
		print("salvando id")
		idmessageagenda = client.send_message(message.chat.id, message.id, agenda).id
		executa_query(f"UPDATE valores SET valor = {idmessageagenda} WHERE id = 2", "update")
	else:
		print("nao salvou")
		client.send_message(message.chat.id, agenda)
	
@brinabot.on_message(filters.chat([STAFF, TESTES]) & filters.command("vcalendario"))
def comando_formatacalendario(client, message):
	agenda = formata_calendario()
	client.send_message(message.chat.id, agenda)

@brinabot.on_message(filters.chat([STAFF, TESTES]) & filters.command("agenda"))
def comando_salvaagenda(client, message):
	global idmessageagenda
	jogos = message.text.replace("/agenda", "")
	if jogos:
		resultado = salva_agenda(jogos)
		if len(resultado) < 20:
			agenda = formata_agenda(True)
			client.edit_message_text(message.chat.id, idmessageagenda, agenda)
			client.send_message(message.chat.id, "Jogos agendados com sucesso.", reply_to_message_id = idmessageagenda)

		else:
			client.send_message(message.chat.id, resultado)

@brinabot.on_message(filters.chat([STAFF, TESTES]) & filters.command("filters"))
def comando_formatafilters(client, message):
	formata_calendario(True)

@brinabot.on_message(filters.chat([STAFF, TESTES]) & filters.command("horarios"))
def comando_horarios(client, message):
	horarios = horas_disponiveis()
	if message.reply_to_message:
		client.edit_message_text(message.chat.id, message.reply_to_message.id, horarios)
		return
	client.send_message(message.chat.id, horarios)
	
@brinabot.on_message(filters.user(AUTORIZADOS) & filters.command("sqlagenda", prefixes=list("/.!")))
def comando_sqlagenda(client, message):
	comando = message.text.replace(".sqlagenda ", "").replace("/sqlagenda ", "")
	try:
		conn = sqlite3.connect("agenda.db")
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
				message.reply(f"Comando executado com sucesso.\n\n<code>{comando}</code>")

		conn.close()
	except Exception as e:
		 client.edit_message_text(message.chat.id, message.id, e)
		 

		 
		 		 		 
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
#conn = sqlite3.connect('agenda.db')

# Criar um cursor para executar comandos SQL
#cursor = conn.cursor()

@brinabot.on_message(filters.chat([STAFF, TESTES]) & filters.command("dagenda"))
def comando_apagaagenda(client, message):
    try:
        with sqlite3.connect('agenda.db') as conn:
            # Criar um cursor para executar comandos SQL
            cursor = conn.cursor()
        
            # Executar a consulta de exclusão
            cursor.execute("DELETE FROM agenda WHERE fixo is NULL")
        
            # Confirmar as alterações no banco de dados
            conn.commit()
        
            # Fechar automaticamente a conexão quando o bloco 'with' for concluído
            client.send_message(message.chat.id, "Agenda resetada.")
    except sqlite3.Error as e:
        client.send_message(message.chat.id, f"Erro no SQLite: {e}")
    except Exception as ex:
        client.send_message(message.chat.id, f"Ocorreu uma exceção: {ex}")
		
@brinabot.on_message(filters.chat([STAFF, TESTES]) & filters.command("daplicador"))
def comando_removeagenda(client, message):
	conn = sqlite3.connect('agenda.db')
	cursor = conn.cursor()
	#aplicador = message.text.split()[1] or ""
	aplicador = message.text.replace("/daplicador", "").strip()
	if aplicador:
	
	# Criar um cursor para executar comandos SQL
		cursor.execute(f"DELETE FROM agenda WHERE aplicador = '{aplicador.capitalize()}' AND fixo IS NULL")
		deleted_rows = cursor.rowcount # Obtém o número de linhas deletadas
		if deleted_rows > 0:
			conn.commit()
			conn.close()
			client.send_message(message.chat.id, f"Foram removidos {deleted_rows} jogos de {aplicador} da agenda.")
		else:
			 conn.close()
			 client.send_message(message.chat.id, f"Não foram encontrados jogos agendados para {aplicador}.")

	
def verifica_jogo_existente(cursor, game, semana, hora):
    cursor.execute("SELECT COUNT(*) FROM agenda WHERE (semana = ? AND jogo = ? AND fixo IS NULL)", (semana, game))
    countjogo = cursor.fetchone()[0]
    if countjogo:
        conflito = "jogo"
        return conflito
    else:
        cursor.execute("SELECT COUNT(*) FROM agenda WHERE (semana = ? AND hora = ? AND fixo IS NULL)", (semana, '('+hora+')'))
        counthora = cursor.fetchone()[0]
        if counthora:
            conflito = "hora"
            return conflito
    return False
   
def verifica_jogo_vazio(cursor, semana, hora):
    cursor.execute("SELECT COUNT(*) FROM agenda WHERE (semana = ? AND jogo = 'Vazio' AND hora = ?)", (semana, '('+hora+')'))
    count = cursor.fetchone()[0]
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
				aplicador = jogo.split(" ")[-1].replace(":", "").capitalize()
				aplicador_definido  = True
				jogos_errados += f"❌ Erro ao agendar\n\n"
			else:
				try: 
					dados_do_jogo = jogo.split(" - ",1)
					dia_semana, hora = dados_do_jogo[0].split(" ")
					if len(dados_do_jogo) > 1:
						nome_do_jogo = demoji.replace(dados_do_jogo[1], "").strip()
						nome_do_jogo = nome_do_jogo[0].upper() + nome_do_jogo[1:].lower()
					else:
						nome_do_jogo = "Vazio"
				except Exception as Error:
					jogos_errados += f"Erro de formatação em {jogo}"
					return jogos_errados
				
				# Formata nome do dia da semana
				if not dia_semana.lower() in ("sábado, sabado, domingo"):
					dia_semana = dia_semana.lower().replace("terca", "terça")
					dia_semana = dia_semana.upper() + "-FEIRA"
				else:
					dia_semana = dia_semana.upper().replace("SABADO", "SÁBADO")
				
				for nome_correto in all_jogos:
					if is_input_accepted(nome_do_jogo, nome_correto[0]):
						nome_do_jogo = nome_correto[0]
				conflito = verifica_jogo_existente(cursor, nome_do_jogo, dia_semana, hora)
				if verifica_jogo_vazio(cursor, dia_semana, hora):
					sql = f"UPDATE agenda SET jogo = '{nome_do_jogo}' WHERE semana = '{dia_semana}' AND hora = '({hora})'"
					cursor.execute(sql)
					conn.commit()				
				elif conflito == "jogo":
					jogos_errados += f"{nome_do_jogo} já foi agendado {dia_semana.capitalize()}\n"
				elif conflito == "hora":
					jogos_errados += f"{dia_semana.capitalize()} {hora} não está disponível\n"
				elif not conflito:
					sql = f"INSERT INTO agenda(aplicador, jogo, semana, hora) VALUES ('{aplicador}', '{nome_do_jogo}', '{dia_semana}', '({hora})')"
					cursor.execute(sql)
					conn.commit()
				else:
					pass
	conn.close()
	return jogos_errados
	
dias_da_semana = [
	    "SEGUNDA-FEIRA",
	    "TERÇA-FEIRA",
	    "QUARTA-FEIRA",
	    "QUINTA-FEIRA",
	    "SEXTA-FEIRA",
	    "SÁBADO",
	    "DOMINGO"
]

def horas_disponiveis():
	conn = sqlite3.connect('agenda.db')
# Criar um cursor para executar comandos SQL
	cursor = conn.cursor()
	
	cursor.execute("SELECT semana, hora FROM agenda WHERE jogo != 'Jogo do lobo'")
	jogos = cursor.fetchall()
	disponiveis = "✳️ Horários disponíveis"
	ocupado = 0
	teste = 0
	for dia in dias_da_semana:
		disponiveis += f"\n\n• {dia}\n\n"
		for hora in range(13, 24):
			for jogo in jogos:
				#print(jogo[3], jogo[4][1:3])
				try:
					if jogo[0] == dia and int(jogo[1][1:3]) == hora:
						ocupado = 1
						if teste:
							disponiveis =disponiveis[:-1] + "jogo rapido até 1h\n"
							teste = 0
						print(jogo[2])
						break #print("match")
				except:
					pass
			if not ocupado:
				disponiveis += f"➱ {hora}h - \n"
				teste = 1
				
			ocupado = 0
	conn.close()
	return disponiveis
	
def formata_agenda(camps = False):
	conn = sqlite3.connect('agenda.db')

# Criar um cursor para executar comandos SQL
	cursor = conn.cursor()
	agenda = "<b>AGENDA SEMANAL</b> 🗓\n"
	
	i = 0
	for dia in dias_da_semana:
		sql = f"SELECT * FROM agenda WHERE semana = '{dia}' ORDER BY hora, fixo DESC"
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
			cursor.execute(sql)
			emoji = cursor.fetchone()
			if emoji:
				emoji = f"{emoji[0]}"
			elif jogo[2] == "Campeonato de Zumbi":
				emoji = "🧟‍♂"
			elif "Quiz" in jogo[2]:
				emoji = "❓"
			else:
				emoji = "⚠️"
			agenda += f"{emoji} {jogo[2]} {jogo[4]}\n"
		if saves:
			diasave = dia[:-6] if len(dia) > 7 else dia
			brinabot.send_message(TESTES,  "/personal " + diasave.lower() + "\n" + agenda)
			agenda = ""
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
		nome = demoji.replace(jogo[1:], "").strip()
		cursor.execute(f"SELECT jogo FROM jogos WHERE jogo='{nome}'")
		resultado = cursor.fetchone()
		print(resultado)
		# Se o jogo não estiver na tabela, insira-o
		if resultado is None:
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
		# Se o jogo não estiver na tabela, insira-o
		if resultado is None:
			cursor.execute(f"INSERT INTO jogos(emoji, jogo) VALUES ('{emoji}', '{nome}')")
			conn.commit()
	conn.close()

#sql = f"SELECT * FROM jogos"
#cursor.execute(sql)
#print(cursor.fetchall())
# Salvar as alterações e fechar a conexão com o banco de dados
#conn.commit()
#conn.close()
print("init")
