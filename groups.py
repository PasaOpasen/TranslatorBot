
import translator_tools
import random

import telebot

from flask import Flask, request
import os

API_TOKEN = '1146428469:AAGbR6x3n-p-1QJmdQ71aQtoAsFH7lrcSZ8'

bot = telebot.TeleBot(API_TOKEN)
server = Flask(__name__)
PORT = int(os.environ.get('PORT', '8443'))



instructions = """Hello! I'm the translator bot!

I will translate your messages into all chosen languages. After u can reply my answers to your foreign friends!

Also u can reply messages here.

All u need is to choose necessary languages and start messaging!


WARNING: because of free deploy your settings are reset periodically. If u haven't got a translate in 10sec, don't worry, just choose languages again. Fortunately, if u will send message into language not from langlist, this one is added automatically.

IF U USE ME IN GROUP, u should write long messages (to translate) or reply any my message (to translate or set settings from your message) or just reply any another message. 
If u wanna send long message without translation, u should end it by symbol "#", and if u want to translate short message simpler, just end it by "##"

Problems? Questions? Write an issue https://github.com/PasaOpasen/TranslatorBot"""

show_it = 'Show instructions again, bot!'
want_choose = 'Choose languages'

class Chat:
    def __init__(self):
        self.langs = ['ru','en']
        self.counter = 1
        self.present = "U haven't selected languages yet (default Russian+English)"
    def counter_to_default(self):
        self.counter = 1
    def counter_inc(self):
        self.counter += 1
    def counter_equals(self,value):
        return self.counter == value
    def get_current_languages(self):
        if self.langs == ['ru', 'en']:
            return self.present
        return f"Your current langlist is {['+'.join([translator_tools.lang_dic_reversed[i] for i in self.langs])]}"

chats = {}



keyboard1 = telebot.types.ReplyKeyboardMarkup(True,True)
keyboard1.row(show_it, want_choose)

def choice(message):
    mes = ['Supported languages:\n']
    mes.extend([f'{n+1}. {lang}' for n, lang in enumerate(translator_tools.all_langs)])
    inds = [76, 22, 71]#[random.randint(1,100), random.randint(1,100), random.randint(1,100)]
    a, _ = translator_tools.get_langs_from_numbers(inds)
    mes.append(f"""\nU should choose some languages' numbers and write them like '1 2 3' (without quotes).

For example, the answer '{" ".join([str(i) for i in inds])}' means {"+".join(a)}.

{chats[message.chat.id].get_current_languages()}""")

    bot.send_message(message.chat.id, '\n'.join(mes))


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, instructions, reply_markup=keyboard1)
    if message.chat.id not in chats:
        chats[message.chat.id] = Chat()

@bot.message_handler(content_types=['text'])
def send_message_global(message):
    txt = message.text

    if len(txt) < 3:
        return

    if message.chat.id not in chats:
        chats[message.chat.id] = Chat()

    if txt[-1] == '#':
        if txt[-2] == '#':
            send_text_group(message, True)
        else:
            return

    if txt[0] == '/':
        return

    if message.chat.type == 'group' and message.reply_to_message is None:

        if len(txt) > 25:
            send_text_group(message)
            chats[message.chat.id].counter_to_default()
        elif chats[message.chat.id].counter_equals(25):
            bot.send_message(message.chat.id, "don't forget me! 😊")
            chats[message.chat.id].counter_to_default()
        else:
            chats[message.chat.id].counter_inc()
    else:
        send_text(message)

def send_text_group(message, from_short=False):
    txt = message.text
    res = translator_tools.log_text(txt, chats[message.chat.id].langs) if not from_short else translator_tools.log_text(txt[:-2], chats[message.chat.id].langs)
    bot.reply_to(message, '\n'.join(res))

def send_text(message):

    txt = message.text
    if txt[0].isdigit() and txt[-1].isdigit():
        t, chats[message.chat.id].langs = translator_tools.get_langs_from_numbers([int(n) for n in txt.split()])

        if len(t) < 2:
            bot.reply_to(message, "No sense to choose only 1 language. Select more")
            return

        lgs = '+'.join([str(i) for i in t])
        #chats[message.chat.id].present = f"Your current langlist is {lgs}"
        bot.send_message(message.chat.id, f"Good! Your langlist is {lgs}. Now try to send any message")
        return

    if txt == show_it:
        start_message(message)
    elif txt == want_choose:
        choice(message)
    else:
        res = translator_tools.log_text(txt, chats[message.chat.id].langs)
        bot.send_message(message.chat.id, '\n'.join(res))




bot.polling()


@server.route('/' + API_TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://multi-translator-bot.herokuapp.com/' + API_TOKEN)
    return "!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
