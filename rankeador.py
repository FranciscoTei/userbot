from botinit import brinabot

@brinabot.on_message(filters.chat(staff) & (filters.regex("placar") | filters.regex("Placar")))
def pega_placar(client, message):
	pass
class Message:
	self.text = "placar\n\nchico 10 sabrina 15"
	self.text.

def trata_placar(placar):
    placars = message.text.lower().replace()
    client.send_
    
    if texto.startswith("placar"):
        placar = message.text.split("\n")[1:]
        """placar = "\n".join(placar)
		sql = "SELECT texto FROM textos WHERE titulo = 'rankingplacar'"
		placartotal = executa_query(sql,"select")[0][0]
		print(placartotal)
		placartotal += f"{placar}\n"
		client.edit_message_text(ranking, 654587, placartotal)
		sql = f"UPDATE textos SET texto = '{placartotal}' WHERE titulo = 'rankingplacar'"
		executa_query(sql, "update")"""


brinabot.run()