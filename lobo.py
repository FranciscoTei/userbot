import random
import time
from botinit import brinabot
from database import executa_query, sqlite
from info import *
from utils import DateTimeInfo, format_titles_and_links

	
def postando_lobo(chat = LOBINDIE, messageid = False):
	"""
    Envia a postagem do jogo "Lobo" no grupo, exibindo os números dos membros fixos.

    Args:
        chat (int): ID do canal onde será feita a postagem. Valor padrão é lobindie.

    Returns:
        None
	"""
	
		# Obtém o id da imagem atual e a quantidade de pontos atual
	#pontos, idfoto = sqlite.executa("SELECT pontos, idfoto FROM lobo WHERE IR = 1")
	pontos = int(executa_query("SELECT valor FROM valores WHERE nome = 'pontoslobo'", "select")[0][0])
	print(pontos)
	
	#Monta a lista de membros e numeros escolhidos
	sql = "SELECT nomeuser, numero FROM lobo"
	numerosfixos = executa_query(sql, "select")
	lista = ""
	for nome, numero in numerosfixos:
		numero = "{:02d}".format(numero)
		lista = f"{lista}{nome}: {numero}\n"
		
	lobomensagem = executa_query("SELECT texto FROM textos WHERE titulo = 'lobomensagem'",
		"select",
	)[0][0]
	#Monta o texto da postagem
	atualizado = lobomensagem.format(pontos, lista = lista)
	#Posta o lobo no grupo
	if messageid:
		brinabot.edit_message_text(chat, messageid, atualizado)
	else:
		messageid = brinabot.copy_message(chat, IMAGENS, 9, atualizado).id
		# insere a data na tabela lobo
		hoje = DateTimeInfo()
		#sqlite.update(f"UPDATE lobo SET data='{hoje}', idmessage = {messageid}")
		executa_query(f"UPDATE valores SET valor = '{hoje}' WHERE nome = 'datalobo'", "update")
		executa_query(f"UPDATE valores SET valor = {messageid} WHERE nome = 'lobomessageid'", "update")
	#Fixa a postagem
	brinabot.pin_chat_message(chat, messageid)
	

def confere_casa(numero):
	print(numero)
	casa = sqlite.executa(f"SELECT casa FROM casas WHERE numero = {numero}")
	return casa[0]
	
def atualiza_lobo(chat, messageid = False):
	listamembros = executa_query("SELECT nomeuser, numero FROM lobo", "select")[0]
	lista = ""
	for membro, numero in listamembros:
		numero = "{:02d}".format(numero)
		lista = f"{lista}\n {membro}: {numero}"
	
	sql = "SELECT texto FROM textos WHERE titulo = 'lobomensagem'"
	lobomensagem = executa_query(sql, "select")[0]
	sql = "SELECT texto FROM textos WHERE titulo = 'lobofinal'"
	lobofinal = executa_query(sql, "select")[0]
	#Monta o texto da postagem
	atualizado = lobomensagem[0].format(pontos) + lista + lobofinal[0]
	#Posta o lobo no grupo
	if messageid:
		pass
	else:
		messageid = brinabot.copy_message(chat, -1001217627450, pontos[1], atualizado).id
	#Fixa a postagem

def texto_ganhador(situacao, quant, pontos, ganhadores):
	if situacao == "casa":
		pontos = int((pontos//2)//quant)
		if quant == 1:
			return f"Parabéns, {ganhadores}!! 🥳\nUm número do mesmo item que o seu foi sorteado e você ganhou {pontos} pontos 🤑.", pontos
		else:
			return f"Parabéns, {ganhadores}!! 🥳\nUm número do mesmo item que o seu foi sorteado e vocês ganharam {pontos} pontos 🤑.", pontos
	else:
		pontos = int(pontos/quant)
		if quant == 1:
			return f"Parabéns, {ganhadores}!! 🥳\nO número escolhido por você foi sorteado e você ganhou {pontos} pontos 🤑.", pontos
		else:
			return f"Parabéns, {ganhadores}!! 🥳\nO número escolhido por você foi sorteado e vocês ganharam {pontos} pontos 🤑.", pontos

def sorteando_lobo(chat = LOBINDIE):
	"""
    Realiza o sorteio do jogo 'lobo' e exibe os ganhadores.

    Args:
        chat (str): O chat em que as mensagens serão enviadas.

    Returns:
        None
	"""
	sorteado = random.randint(0,99)
	idmessage = int(executa_query("SELECT valor FROM valores WHERE nome = 'lobomessageid'", "select")[0][0])
	brinabot.send_message(chat, f"❗️<b>Número sorteado:</b> <code>{sorteado}</code>", reply_to_message_id = idmessage)
	message = brinabot.send_message(chat, "<b>Procurando ganhadores.</b>")
	for i in (2,3):
		time.sleep(1)
		brinabot.edit_message_text(chat, message.id, f"<b>Procurando ganhadores{i*'.'}</b>")
	
	ganhadorexato = executa_query(f"SELECT iduser, nomeuser, username FROM lobo WHERE numero = {sorteado}", "select")
	casa = confere_casa(sorteado)
	ganhadorcasa = executa_query(f"SELECT iduser, nomeuser, username FROM lobo WHERE casa = '{casa}'", "select")

	#pontos, idmessage = sqlite.executa("SELECT pontos, idmessage FROM lobo")
	pontos = int(executa_query("SELECT valor FROM valores WHERE nome = 'pontoslobo'", "select")[0][0])
	#idmessage = int(executa_query("SELECT valor FROM valores WHERE nome = 'lobomessageid'", "select"))
	brinabot.unpin_chat_message(chat, idmessage)
	
	try:
		if not ganhadorexato and not ganhadorcasa:
			brinabot.edit_message_text(chat, message.id, f"""Ninguém ganhou! 😕
🤑 <b>Prêmio acumulado:</b> {pontos+5} pontos """)
			atualiza_pontos_lobo(0, pontos)
			encerra_lobo()
			return
		if ganhadorexato:
			ganhadores = format_titles_and_links(ganhadorexato)
			texto, pontosplacar = texto_ganhador('exato',len(ganhadorexato), pontos, ganhadores)
			atualiza_pontos_lobo(1, pontos)
			placarlobo = ' '.join([f"{nome[1]} {pontosplacar}" for nome in ganhadorexato])
		else:
			ganhadores = format_titles_and_links(ganhadorcasa)
			texto, pontosplacar = texto_ganhador('casa',len(ganhadorcasa), pontos, ganhadores)
			atualiza_pontos_lobo(0, pontos)
			placarlobo = ' '.join([f"{nome[1]} {pontosplacar}" for nome in ganhadorcasa])

		brinabot.edit_message_text(
			chat, message.id,
			texto
		)

		brinabot.send_message(STAFF, f"placar\n\n{placarlobo}")

	except Exception as Erros:
		brinabot.send_message(LOGS, Erros)
	finally:
		encerra_lobo()
			

def atualiza_pontos_lobo(case, pontos):
	novapontuacao = [pontos + 5, 5]
	#sqlite.executa(f"UPDATE lobo SET pontos = {novapontuacao[case]}")
	executa_query(f"UPDATE valores SET valor = {novapontuacao[case]} WHERE nome = 'pontoslobo'", "update")

	
def encerra_lobo():
	executa_query("DELETE FROM lobo WHERE fixo = 0", "delete")
	#sqlite.update("UPDATE lobo SET idmessage = 0")
	executa_query("UPDATE valores SET valor = 0 WHERE nome = 'lobomessageid'", "update")

if __name__ == "__main__":
	with brinabot:
		sorteando_lobo()

	
