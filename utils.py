import datetime
from collections import Counter
from database import executa_query
import random
import time
from botinit import brinabot
import sqlite3
from info import LOBINDIE

class Modulos:
    def __init__(self):
        status = executa_query(
        	f"SELECT * FROM modulos WHERE grupoid = '{LOBINDIE}'", "select", True
        )[0]
        self.ps= status["palavra_secreta"]
        self.lobo = status["lobo"]
        self.quiz = status["quiz"]
        self.call = status["callmembros"]
        self.aniver = status["aniver"]
        self.tenthings = status["tenthings"]

    def postar_lobo(self, funcao_lobo):
    	if self.lobo:
    		funcao_lobo()
    
    def postar_ps(self, funcao_ps):
    	if self.ps:
    		funcao_ps()
    		
    def postar_call(self, funcao_call):
    	if self.call:
    		funcao_call()

    def postar_aniver(self, funcao_aniver):
    		if self.aniver:
    			funcao_aniver()
    		
    def postar_tenthings(self, funcao_tenthings):
    		if self.tenthings:
    			funcao_tenthings()
modulo = Modulos()

def call(chatid = False, mensagem = False):
	sql = "SELECT username FROM membros WHERE username NOT LIKE '%bot%'"
	membros = executa_query(sql, "select")
	membros = list(membros)
	random.shuffle(membros)
	for membro in membros:
		if modulo.call is False:
			brinabot.send_message(chatid, "A call foi cancelada.")
			break
		brinabot.send_message(chatid, f"{membro[0]} {mensagem}")
		time.sleep(random.randint(1,2))

def placar_quiz(resultado, client):
	resultado = resultado.replace("  ", " ")  # Remove double spaces
	resultado = resultado.replace("\n ", "\n")  # Remove leading space on each line
	linhas = resultado.splitlines()[4:-2]  # Remove the first two lines
	placar = ""
	for linha in linhas:
		_, jogador, _, pontos, *_ = linha.split(" ")
		pontos = int(pontos) * 3
		if jogador.startswith("@"):
			try:
				time.sleep(0.2)
				membro = client.get_chat_member(-1001366864342, f"{jogador}")
				
				nome_membro = dict_membros.get(membro.user.id, membro.user.first_name)
			except:
				continue
		else:
			nome_membro = jogador

		if pontos > 0:
			placar = f"{placar}{nome_membro} {pontos}\n"
	aplicador_pontos = soma(placar)
	placar = f"{placar}aplicador {aplicador_pontos//5}"
	return placar
	
#soma 
def soma(placar):
	soma = placar.split()
	resultado = 0
	for num in soma:
		if num.isdigit():
			resultado += int(num)
	return resultado
	

	
class DateTimeInfo:
    def __init__(self):
        dt = datetime.datetime.now()
        self.hoje = dt.strftime("%Y-%m-%d")
        self.ano = dt.year
        self.mes = dt.month
        self.dia = dt.day
        self.hora = dt.hour
        self.semana = dt.strftime('%A')
infodata = DateTimeInfo()

def atualizar_membros():
    sql = "SELECT iduser, nomeuser FROM membros"
    membros = executa_query(sql, "select")
    dict_membros = {iduser: nome for iduser, nome in membros}
    return dict_membros
# Executa a função de atualização dos membros uma vez ao iniciar o bot

class MembrosLobindie:
	def __init__(self):
		self.dict= {}
		
	def get_membros(self):
		sql = "SELECT iduser, nomeuser FROM membros"
		membros = executa_query(sql, "select")
		dict_membros = {iduser: nome for iduser, nome in membros}
		self.dict = dict_membros
		return self.dict
			
membroslb = MembrosLobindie()
membroslb.get_membros()

dict_membros = atualizar_membros()

# confere se o chute do usuario esra correto
def conferir_chute(chute, palavras):
	for palavra in palavras:
		if unidecode(palavra.lower()).replace("-"," ") in unidecode(chute.lower()).replace("-"," ") :
			return palavra
	return False
	
	
def list_to_string(lst):
    if len(lst) == 0:
        return " "
    elif len(lst) == 1:
        return lst[0]
    else:
        return " - ".join(lst)

def transform_to_strings(dicas, acertadas):
    dicas_str = list_to_string(dicas)
    acertadas_str = list_to_string(acertadas)
    return dicas_str, acertadas_str


exponents = {1: "", 2: "²", 3: "³", 4: "⁴", 5: "⁵"}


# =============== FUNCOES PALAVRA SECRETA========
def formata_vencedores(vencedores):
	# Conta o número de ocorrências de cada nome na lista de vencedores
	contagem_vencedores = Counter(vencedores)
	# Cria uma nova lista de vencedores sem repetições
	vencedores_unicos = list(set(vencedores))
	
	# Cria uma lista com a string formatada para cada jogador com seus pontos e expoente correspondente
	vencedores_placar= []
	vencedores_str = []
	for vencedor in vencedores_unicos:
	    num_repeticoes = contagem_vencedores[vencedor]
	    exponent = exponents[num_repeticoes]
	    pontos = num_repeticoes * 10
	    vencedores_str.append(f"{vencedor}{exponent}")
	    vencedores_placar.append(f"{vencedor} {pontos}")

	# Cria uma string com a lista de vencedores formatada
	vencedores_str = " ".join(vencedores_str)
	vencedores_placar = " ".join(vencedores_placar)
	
	return vencedores_str, vencedores_placar
	
	
def format_titles_and_links(titles_and_links):
	result = ""
	for i, (iduser, nome, username) in enumerate(titles_and_links):
		membro = username
		try:
			pass
			#membro = f'@{brinabot.get_chat_member(-1001366864342, iduser).user.username}'
		except Exception as e:
			print(e)
		if membro:
			result += f'{membro}'
		else:
			result += f'<a href="tg://user?id={iduser}">{nome}</a>'
		if i == len(titles_and_links) - 2:
			result += " e "
		elif i != len(titles_and_links) - 1:
			result += ", "
	return result


from unidecode import unidecode

if __name__ == "__main__":
	string1 = "témòs Acèntôs"
	string1 = unidecode(string1)
	print(string1)
	vencedotes = ["chico", "chico", "sabrina", "pocoyo"]
	vence = formata_vencedores(vencedotes)
	#num_repeticoes = contagem_vencedores[vencedor]
	#pontos = num_repeticoes * 10


def tratando_param_ps(status, chute, vencedores, acertadas, dicas):
	if status == 1:
		dicas = " "
	else:
		dicas = ', '.join(dicas.values()) if len(dicas) > 1 else next(iter(dicas.values()))
		
	vencedoreslista = vencedores.split(" - ") if vencedores is not None else []
	acertadas = f"{acertadas} - {chute}" if acertadas is not None else chute
	vencedores = formata_vencedores(vencedoreslista)
	
	return vencedores, vencedoreslista, acertadas, dicas
		
