from os import remove
import yt_dlp
from botinit import brinabot
from pyrogram import filters
from info import AUTORIZADOS, TITULAR

counter = 0
@brinabot.on_message(filters.user(AUTORIZADOS) & filters.command("dl"))
def get_text_messages(client, message):
    message.text = message.text.replace("/dl ", "")
    if message.text:
        global counter
        counter += 1
        current_counter = counter
        try:
            if message.from_user.id == TITULAR:
            	brinabot.edit_messagext(message.chat.id, messageid,"carregando.")
            	messageid = message.id
            else:
            	messageid = brinabot.send_message(message.chat.id, 'carregando').id

            try:
                yt_dlp.YoutubeDL({
                    'no_warnings': True,
                    'quiet': True,
                    'outtmpl': 'video{}.mp4'.format(current_counter)
                }).download(message.text)
            except:
                brinabot.edit_messagext(message.chat.id, messageid, "Não foi possível baixar.")
            brinabot.edit_message_text(message.chat.id, messageid, "video baixado")
            brinabot.edit_message_text(message.chat.id, messageid, 'enviando.')
            brinabot.delete_message(message.chat.id, messageid)
            brinabot.send_video(message.chat.id, video=open('video{}.mp4'.format(current_counter), 'rb'))

            remove('video{}.mp4'.format(current_counter))
        except:
            pass
        #brinabot.send_message(message.chat.id, 'Video enviado')
