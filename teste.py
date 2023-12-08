
from pyrogram import Client, filters
import random
import sqlite3

class CRUD:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                user_id INTEGER PRIMARY KEY,
                word TEXT,
                attempts INTEGER DEFAULT 0
            )
        """)
        self.conn.commit()

    def create_player(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO players (user_id) VALUES (?)", (user_id,))
        self.conn.commit()

    def get_player_word(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT word FROM players WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        return result[0] if result else None

    def update_player_word(self, user_id, word):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE players SET word = ? WHERE user_id = ?", (word, user_id))
        self.conn.commit()

    def increase_player_attempts(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE players SET attempts = attempts + 1 WHERE user_id = ?", (user_id,))
        self.conn.commit()

class Wordle:
    def __init__(self, db_file):
        self.crud = CRUD(db_file)
        self.words = ["banana", "carro", "computador", "python", "programacao"]
        self.max_attempts = 5

    def generate_word(self):
        return random.choice(self.words)

    def check_guess(self, word, guess):
        result = ""
        for i in range(len(word)):
            if guess[i] == word[i]:
                result += guess[i]
            elif guess[i] in word:
                result += "?"
            else:
                result += "*"
        return result

    def play(self, user_id, guess):
        word = self.crud.get_player_word(user_id)
        if not word:
            word = self.generate_word()
            self.crud.create_player(user_id)
            self.crud.update_player_word(user_id, word)
        attempts = self.crud.get_player_attempts(user_id)
        if attempts >= self.max_attempts:
            return "Você já atingiu o número máximo de tentativas."

        result = self.check_guess(word, guess)
        self.crud.increase_player_attempts(user_id)
        if result == word:
            self.crud.update_player_word(user_id, None)
            return "Parabéns! Você acertou a palavra!"
        else:
            return result

db_file = "wordle.db"
app = Client("wordle_bot")

@Client.on_message(filters.private)
def play_wordle(client, message):
    wordle = Wordle(db_file)
    user_id = message.from_user.id
    guess = message.text.lower()
    result = wordle.play(user_id, guess)
    client.send_message(message.chat.id, result)

app.run()