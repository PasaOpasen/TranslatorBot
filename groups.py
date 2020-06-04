
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

IF U USE ME IN GROUP, u should write long messages (to translate) or reply any my message (to translate or set settings from your message)

Problems? Questions? Write an issue https://github.com/PasaOpasen/TranslatorBot"""

show_it = 'Show instructions again, bot!'
want_choose = 'Choose languages'
#default = 'Set English + Russian'

my_langs = ['ru','en']

counter = 1

present = "U haven't selected languages yet (default Russian+English)"

keyboard1 = telebot.types.ReplyKeyboardMarkup(True,True)
keyboard1.row(show_it, want_choose)

def choice(id):
    mes = ['Supported languages:\n']
    mes.extend([f'{n+1}. {lang}' for n, lang in enumerate(translator_tools.all_langs)])
    inds = [76, 22, 71]#[random.randint(1,100), random.randint(1,100), random.randint(1,100)]
    a, _ = translator_tools.get_langs_from_numbers(inds)
    mes.append(f"""\nU should choose some languages' numbers and write them like '1 2 3' (without quotes).

For example, the answer '{" ".join([str(i) for i in inds])}' means {"+".join(a)}.

{present}""")

    bot.send_message(id, '\n'.join(mes))


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, instructions, reply_markup=keyboard1)
    #bot.reply_to(message, "Hi there, I am EchoBot.")


@bot.message_handler(content_types=['text'])
def send_message_global(message):
    if message.chat.type == 'group' and message.reply_to_message is None:
        global counter
        #print(message)

        if len(message.text) > 15:
            send_text_group(message)
            counter = 1
        elif counter % 10 == 0:
            bot.send_message(message.chat.id, "don't forget me!")
            counter = 1
        else:
            counter += 1
    else:
        send_text(message)

def send_text_group(message):
    txt = message.text
    res = translator_tools.log_text(txt, my_langs)
    bot.reply_to(message, '\n'.join(res))

def send_text(message):

    txt = message.text
    if txt[0].isdigit() and txt[-1].isdigit():
        global my_langs, present
        t, my_langs = translator_tools.get_langs_from_numbers([int(n) for n in txt.split()])

        if len(t) < 2:
            bot.reply_to(message, "No sense to choose only 1 language. Select more")
            return

        lgs = '+'.join([str(i) for i in t])
        present = f"Your current langlist is {lgs}"
        bot.send_message(message.chat.id,f"Good! Your langlist is {lgs}. Now try to send any message")
        return

    if txt == show_it:
        start_message(message)
    elif txt == want_choose:
        choice(message.chat.id)
    else:
        res = translator_tools.log_text(txt, my_langs)
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
