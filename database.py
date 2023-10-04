import pymysql
import sqlite3
from info import *
from botinit import trata_erro


con = pymysql.connect(host=HOST, user=USER,password=PASSWORD,database = DATABASE)

def executa_query(query, tipo, cursor_dict=False):
	if con.open is False:
		con.ping()
	cursor_class = pymysql.cursors.DictCursor if cursor_dict else pymysql.cursors.Cursor
	cursor = con.cursor(cursor_class)
	if tipo == "select":
		cursor.execute(query)
		resultado = cursor.fetchall()
		return resultado
	if tipo in ("insert", "update", "delete"):
		cursor.execute(query)
		con.commit()
	cursor.close()
	
class SQLite:
	def __init__(self):
		self.database = "lobo_postado.db"
	
	def executa(self, query):
		try:
			with sqlite3.connect(self.database) as conn:
				cursor = conn.cursor()
				cursor.execute(query)
				resultado = cursor.fetchone()
		except sqlite3.Error as e:
			return e
		return resultado
	
	def executamany(self, query, quant):
		try:
			with sqlite3.connect(self.database) as conn:
				cursor = conn.cursor()
				cursor.execute(query)
				resultado = cursor.fetchmany(quant)
		except sqlite3.Error as e:
			return e
		return resultado

	def executaall(self, query):
		try:
			with sqlite3.connect(self.database) as conn:
				cursor = conn.cursor()
				cursor.execute(query)
				resultado = cursor.fetchall()
		except sqlite3.Error as e:
			return e
		return resultado
		
	def update(self, query):
		try:
			with sqlite3.connect(self.database) as conn:
				cursor = conn.cursor()
				cursor.execute(query)
				conn.commit()
		except sqlite3.Error as e:
			return e
		return True

	def delete(self, query):
		try:
			with sqlite3.connect(self.database) as conn:
				cursor = conn.cursor()
				cursor.execute(query)
				conn.commit()
		except sqlite3.Error as e:
			return e
		return True

sqlite = SQLite()