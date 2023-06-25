from info import *
from database import executa_query
from utils import DateTimeInfo, membroslb, infodata, formata_vencedores
from botinit import brinabot
import json


def postando_palavra_secreta(chat = LOBINDIE):
	'''
    Função responsável por postar a palavra secreta no chat.

    Parâmetros:
    - brinabot: Cliente do bot.
    - chat: ID do chat onde a palavra secreta será postada.

    Retorna:
    retorna as palavras sorteadas.
    '''
    #solicitando dados do palavra secreta
    #Sorteando um tema para o palavra secreta
	tema = executa_query('SELECT tema FROM palavra_secreta WHERE postado = (SELECT MIN(postado) FROM palavra_secreta) ORDER BY RAND () LIMIT 1', 'select')[0]
	#sorteando as palavras com o tema sorteado
	palavras = executa_query(f"SELECT tema, palavras, dicas FROM palavra_secreta WHERE postado = (SELECT MIN(postado) FROM palavra_secreta) AND tema = \'{tema[0]}\' ORDER BY RAND() LIMIT 5;", 'select')
	print('palavras cruas do sql', palavras)
	#revisar
	#sql = f"UPDATE palavra_secreta SET postado = postado + 1 WHERE tema = '{tema[0]}'"
	#executa_query(sql, "update")
	
	#transformando em dict e depois string para salvar no banco de dados
	ps.palavras = {subtupla[1]: subtupla[2] for subtupla in palavras}
	palavrasecreta = str(ps.palavras).replace("'",'"')
	executa_query(f"INSERT INTO palavra_teste (tema, palavras) VALUES ('{tema[0]}','{palavrasecreta}')", "insert")
	
	#buscanco o texto da postagem
	textopalavrasecreta = executa_query("SELECT texto FROM textos WHERE titulo = 'palavrasecreta'", 'select')[0]
	#postando o palavra secreta no grupo
	message = brinabot.send_message(
		chat,
		textopalavrasecreta[0].format(
			tema = tema[0],
			vencedores = " ",
			palavras = " ",
			dicas = " ",
			pontos = 10
		)
	)
	brinabot.pin_chat_message(chat, message.id)
	
	#salvando o id da postagem para futuras edições
	infodata = DateTimeInfo()
	sql = f"UPDATE palavra_teste SET idmessage = {message.id}, status = 1, Data = '{infodata.hoje}' ORDER BY id DESC LIMIT 1;"
	executa_query(sql, "update")
	return ps.palavras
	

def palavra_secreta(usuario, chute, messageid, chat = LOBINDIE):
	"""
    Função que lida com o acerto da palavra secreta.

    Args:
        usuario (objeto): Objeto que representa o usuário que acertou a palavra.
        chute (str): Palavra que foi acertada.
        messageid (int): ID da mensagem do Telegram.
        chat (int, opcional): ID do chat onde a palavra secreta está sendo jogada.

    Returns:
        dict ou None: Dicionário contendo as palavras secretas atualizadas se ainda houver palavras restantes,
        caso contrário, retorna None.

	"""
	#solicitando dados do palavra secreta
	palavrasecreta = executa_query(
		"SELECT * FROM palavra_teste ORDER BY id DESC LIMIT 1",
		"select",
		True
	)[0]

	#enviando mensagem de acerto
	brinabot.send_message(chat, 
		text = """✅ <b>Palavra correta.</b>

Parabéns, você ganhou 10 pontos! 🤑""",
		reply_to_message_id=messageid
	)

	#recuperando nome do usuario
	nome_membro=membroslb.dict.get(usuario.id, usuario.first_name)

			
	#trabalhando vencedores
	vencedoreslista = palavrasecreta["vencedores"].split(" - ") if palavrasecreta["vencedores"] else []
	vencedoreslista.append(nome_membro)
	vencedores, _= formata_vencedores(vencedoreslista)

	
	#tranalhando acertadas
	acertadas = f"{palavrasecreta['acertadas']} - {chute}" if palavrasecreta["acertadas"] else chute

	#trabalhando palavras
	ps.palavras.pop(chute)
		
	#trabalhando dicas
	if palavrasecreta["status"] == 1:
		dicas = " "
	else:
		dicas = ', '.join(ps.palavras.values()) if len(ps.palavras) > 1 else next(iter(ps.palavras.values()))

	#buscanco o texto da postagem
	sql = "SELECT texto FROM textos WHERE titulo = 'palavrasecreta'"
	textopalavrasecreta = executa_query(sql, "select")[0]
			
	# Atualiza a mensagem no Telegram
	brinabot.edit_message_text(
		chat,
		palavrasecreta["idmessage"],
		textopalavrasecreta[0].format(
			tema = palavrasecreta["tema"],
			vencedores = vencedores,
			palavras = acertadas,
			dicas = dicas,
			pontos = 10
		)
	)

	#atualiza o banco de dados
	savevencedores = ' - '.join(vencedoreslista)
	sql = f"UPDATE palavra_teste SET palavras=NULLIF('{json.dumps(ps.palavras)}', ''), vencedores='{savevencedores}', acertadas='{acertadas}' WHERE idmessage={palavrasecreta['idmessage']}"
	executa_query(sql, "update")
	if ps.palavras:
		return ps.palavras
	else:
		palavra_secreta_finalizada(chat)


def dicas_ativadas(chat = LOBINDIE):
	"""
    Envia mensagem informando que as dicas foram ativadas e atualiza a mensagem da palavra secreta com as informações atualizadas.

    Args:
        chat (int, opcional): ID do chat onde as dicas foram ativadas.

	"""
	if not ps.palavras:
		return

	palavrasecreta = executa_query(
		f"SELECT * FROM palavra_teste ORDER BY id DESC LIMIT 1",
		'select', 
		True
	)[0]
    
	mensagem = '⚠ | <b>Dicas liberadas.</b>\n  \n Boa sorte a todos! 🥰'
	brinabot.send_message(chat, mensagem, reply_to_message_id=palavrasecreta["idmessage"])
    
	#trabalhando parametros
	dicas = ', '.join(ps.palavras.values()) if len(ps.palavras) > 1 else next(iter(ps.palavras.values()))
    
	tema = palavrasecreta['tema']
    
	vencedoreslista = palavrasecreta['vencedores'].split(' - ') if palavrasecreta['vencedores'] else []
    
	acertadas = palavrasecreta['acertadas'] if palavrasecreta['acertadas'] else ' '
    
	vencedores, _ = formata_vencedores(vencedoreslista)
    
	#obtendo texto da postagem
	textopalavrasecreta = executa_query(
		"SELECT texto FROM textos WHERE titulo = 'palavrasecreta'",
   	'select')[0]
   	
	#Atualiza a mensagem no Telegram
	brinabot.edit_message_text(
		chat, 
		palavrasecreta['idmessage'], 
		textopalavrasecreta[0].format(
			tema = tema,
			vencedores = vencedores,
			palavras = acertadas, 
			dicas = dicas, 
			pontos = 10
		)
	)
	sql = f"UPDATE palavra_teste SET status = 2 WHERE idmessage = {palavrasecreta['idmessage']}"
	executa_query(sql, "update")


def palavra_secreta_finalizada(chat = LOBINDIE):
	"""
    Envia uma mensagem informando que a palavra secreta foi finalizada e atualiza o status no banco de dados.

    Args:
        chat (int, opcional): ID do chat onde a palavra secreta foi finalizada.

	"""
	palavrasecreta = executa_query(
		'SELECT idmessage, status, acertadas, vencedores, tema FROM palavra_teste ORDER BY id DESC LIMIT 1',
		'select', 
		True
	)[0]
	acertadas = palavrasecreta['acertadas'].split(" - ") if palavrasecreta['acertadas'] else ' '
	if palavrasecreta["vencedores"]:
		vencedoreslista = palavrasecreta['vencedores'].split(' - ')
		_, vencedoresplacar = formata_vencedores(vencedoreslista)
		mensagem = f"placar\n\n{vencedoresplacar}"
		brinabot.send_message(STAFF, mensagem) 
		for acertada in acertadas:
			sql = f"DELETE FROM palavra_secreta WHERE palavras = '{acertada}'"
			#revisar
			executa_query(sql, "delete")
		
	brinabot.send_message(chat, "<b>Dinâmica encerrada! ⌛️</b>", reply_to_message_id=palavrasecreta['idmessage'])
	
	sql = f"UPDATE palavra_teste SET status = 0 WHERE idmessage = {palavrasecreta['idmessage']}"
	executa_query(sql, "update")
	sql = f"UPDATE palavra_secreta SET tema = tema+1 WHERE tema = '{palavrasecreta['tema']}'"
	executa_query(sql, "update")
	ps.palavras = {}
	return


def verifica_palavra_postado(chat = LOBINDIE):
	"""
    Verifica se é necessário postar a palavra secreta com base na data e hora atual.

    Args:
        chat (int, opcional): ID do chat onde a palavra secreta será postada.

    Returns:
        dict: Um dicionário contendo as palavras secretas se for necessário postá-las, caso contrário, um dicionário vazio.

	"""
	# obtém o nome do dia da semana correspondente ao número
	if infodata.semana in ('Tuesday', 'Thursday', 'Saturday'):
		comando = "SELECT data, status FROM palavra_teste ORDER BY id DESC LIMIT 1;"
		infops = executa_query(comando, "select")[0]
		diapalavra = infops[0].strftime("%Y-%m-%d")
		if infodata.hoje != diapalavra:
			with brinabot:
				return postando_palavra_secreta(chat)
		else:
			if infops[1]:
				sql = f"SELECT palavras FROM palavra_teste ORDER BY id DESC LIMIT 1"
				ps.palavras = json.loads(executa_query(sql, "select")[0][0])
				return ps.palavras
			else:
				return {}


class PalavraSecreta:
    def __init__(self):
        self.palavras = { }

    def update_palavras(self):
        self.palavras = verifica_palavra_postado()
        return self.palavras
ps = PalavraSecreta()
ps.update_palavras()
#palavras_secretas = verifica_palavra_postado()
#print(palavras_secretas)
