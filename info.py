import os

	
hostfixo = 'uyu7j8yohcwo35j3.cbetxkdyhwsb.us-east-1.rds.amazonaws.com'
userfixo = 'h2xwhmugacxbwv79'
passwordfixo ='mfuwh70z5pjq0jwb'
databasefixo = 'q6p5up8xhrrbmyq0'


#Bot information
API_HASH = os.getenv('api_hash', "60914433b8f4fde57c6ba475f572f912")
API_ID = os.getenv('api_id', "28357147")
NUMBER = os.getenv('number', "+5511950891476")
SESSION = os.getenv('session', False)

#SQL information
HOST = os.getenv('host', hostfixo)
USER = os.getenv('user', userfixo)
PASSWORD=os.getenv('password', passwordfixo)
DATABASE = os.getenv('database', databasefixo)

def define_grupo():
	if TITULAR == 886429586:
		LOBINDIE = -1001366864342
		STAFF = -1001572420135
		TESTES = -1001217627450
		DONO = "Sabrina"
		
	else:
		LOBINDIE = -1001974320965
		STAFF = -1001217627450
		TESTES = -1001974320965
		DONO = "Chico"
		
	return LOBINDIE, STAFF, TESTES
		
#Admins, Channels & Users
LOGS= -1001865449571
if SESSION:
	TITULAR = 886429586
	BOTPASS = "chicobalofo"
	DONO = "Sabrina"
else:
	TITULAR = 934735022
	BOTPASS = "6789"
	DONO = "Chico"

AUTORIZADOS = [836445988, 934735022, 934923747, 886429586]
LOBINDIEFIXO= -1001366864342
LOBINDIE, _, _= define_grupo()#mudar
_, _, TESTES = define_grupo()
INDIECANAL= -1001484956109
INDIEMUSIC = "-1001302341410"
_, STAFF, _= define_grupo() #mudar
RANKING = -423539628
IMAGENS = -1001984560446

