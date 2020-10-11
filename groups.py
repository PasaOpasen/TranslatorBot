
import translator_tools
from translator_tools import from_code_to_name
import random

import telebot

from flask import Flask, request
import os

TESTING = True
DEPLOY = not TESTING

if TESTING:
    API_TOKEN = '1059809966:AAHfjWbOyF3h-F_UZi6krWylOHvA7W3SGE4'
else:
    API_TOKEN = '1146428469:AAGbR6x3n-p-1QJmdQ71aQtoAsFH7lrcSZ8'



bot = telebot.TeleBot(API_TOKEN)
server = Flask(__name__)
PORT = int(os.environ.get('PORT', '8443'))


border = 30

instructions = f"""Hello!!! I'm the *translator bot*! 😌

I will translate your messages in all chosen languages. After u can reply my answers to your foreign friends!

Also u can reply messages here. I will translate them!

All u need is to choose necessary languages and start messaging! 😉

*IF U USE ME IN GROUP*, there are several rules: 😲
  1) replied messages are translated by default
  2) messages longer than {border} symbols are translated by default
    
  3) if the message *SHOULD BE TRANSLATED* then end it by '##'
  4) if the message *SHOULD NOT BE TRANSLATED* then end or start it by '#'
    
  5) _if u wanna get better translation_, end message by '##+' (but it takes time)
    
  6) please, *use correct words* otherwise the language of your message can be recognized wrong

😓 *WARNING*: because of free deploy your settings are reset periodically (when u don't use bot during some hours maybe).
If u haven't got a translate in 10sec, don't worry, just choose languages again or write '/start' command.
😁 Fortunately, if u will send message into language not from language list, this one is added automatically.

*Problems? Questions? Advice?* Write an issue https://github.com/PasaOpasen/TranslatorBot 😏"""


show_it = 'Show instructions again, bot!'
want_choose = 'Choose languages'
want_delete = 'Remove excess languages'
go_to_english = 'Go to only english'


class Chat:
    def __init__(self, chat_id):
        self.langs = ['ru','en']
        self.counter = 1
        self.present = "U have default settings (_Russian+English_)"
        self.id = chat_id
        print(f"---------> new chat with id = {id}")
        self.used = {}
    def counter_to_default(self):
        self.counter = 1
    def counter_inc(self):
        self.counter += 1
    def counter_equals(self,value):
        return self.counter == value
    
    def get_current_languages(self):
        if self.langs == ['ru', 'en']:
            return self.present
        return f"Your current language list is {'+'.join([translator_tools.lang_dic_reversed[i] for i in self.langs])}"

    def increment_used(self):
        for l in self.langs:
            if l in self.used:
                self.used[l] += 1
            else:
                self.used[l] = 0

    def correct_used(self):
        
        
        total = sum(self.used.values())
        percents = [val/total for val in self.used.values()]
        res = []
        lg = []
        for (lang, count), percent in zip(self.used.items(), percents):
            g = from_code_to_name(lang)
            if count == 0:
                res.append(f'_delete {g} language because of only 1 time usage_')
                lg.append(lang)
            elif percent < 0.1:
                res.append(f'_delete {g} language because of it is just {percent:.2%} < 10% of usage_')
                lg.append(lang)

        for lang in lg:
            del self.used[lang]
            self.langs.remove(lang)

        st = f'_Cannot detect excess languages_, your current counter is {self.used}' if len(res) == 0 else '\n'.join(res)

        bot.send_message(self.id, st, reply_markup=keyboard1, parse_mode='Markdown')

    def get_count_of_langs(self):
        return len(self.langs)
    
    def to_english(self):
        self.langs = ['en']
        self.used = {
            'en': 0
            }



# database of chats
chats = {}



keyboard1 = telebot.types.ReplyKeyboardMarkup(True,True)
keyboard1.row(show_it, want_choose)
keyboard1.row(go_to_english)

keyboard2 = telebot.types.ReplyKeyboardMarkup(True,True)
keyboard2.row(show_it, want_choose)
keyboard2.row(go_to_english)
keyboard2.row(want_delete)


message_for_choice = ['*Supported languages*:\n'] + [f'{n+1}. {lang}' for n, lang in enumerate(translator_tools.all_langs)]

def choice(message):

    inds = [76, 22, 71]#[random.randint(1,100), random.randint(1,100), random.randint(1,100)]
    a, _ = translator_tools.get_langs_from_numbers(inds)
    mes = f"""\n*U should choose some languages' numbers from this list and write them like* '_1 2 3_' (without quotes).

For example, the answer '{" ".join([str(i) for i in inds])}' means *{"+".join(a)}*

{chats[message.chat.id].get_current_languages()}"""

    bot.send_message(message.chat.id, '\n'.join(message_for_choice + [mes]), parse_mode='Markdown')


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, instructions, reply_markup=keyboard1, parse_mode='Markdown')
    if message.chat.id not in chats:
        chats[message.chat.id] = Chat(message.chat.id)

@bot.message_handler(content_types=['text'])
def send_message_global(message):
    txt = message.text

    if len(txt) < 3:
        return

    if message.chat.id not in chats:
        chats[message.chat.id] = Chat(message.chat.id)

    if txt[-1] == '#':
        if txt[-2] == '#':
            send_text_group(message, True)
        return

    if txt.endswith('##+'):
        send_text_group_better(message)
        return


    if txt[0] in ['#', '/'] or txt.startswith('htt'):
        return


    if message.chat.type == 'group' and message.reply_to_message is None:

        if len(txt) > border:
            send_text_group(message)
            chats[message.chat.id].counter_to_default()
        elif chats[message.chat.id].counter_equals(40):
            bot.send_message(message.chat.id, "*don't forget me!* 😊", parse_mode='Markdown')
            chats[message.chat.id].counter_to_default()
        else:
            chats[message.chat.id].counter_inc()
    else:
        send_text(message)


def send_text_group(message, from_short = False):
    
    k = chats[message.chat.id].get_count_of_langs()

    txt = message.text
    res = translator_tools.log_text(txt, chats[message.chat.id].langs) if not from_short else translator_tools.log_text(txt[:-2], chats[message.chat.id].langs)
    
    chats[message.chat.id].increment_used()
    if chats[message.chat.id].get_count_of_langs() > k:
        bot.reply_to(message, '\n'.join(res), reply_markup=keyboard2, parse_mode='Markdown')
    else:
        bot.reply_to(message, '\n'.join(res), parse_mode='Markdown')

def send_text_group_better(message):
    k = chats[message.chat.id].get_count_of_langs()

    txt = message.text
    res = translator_tools.log_text_better(txt[:-3], chats[message.chat.id].langs)
    chats[message.chat.id].increment_used()

    if chats[message.chat.id].get_count_of_langs() - k:
        bot.reply_to(message, '\n'.join(res), reply_markup=keyboard2, parse_mode='Markdown')
    else:
        bot.reply_to(message, '\n'.join(res),parse_mode='Markdown')

    print(f'----------> message from chat {message.chat.id} with langs {chats[message.chat.id].langs}')


def send_text(message):

    txt = message.text
    
    if txt[0].isdigit() and txt[-1].isdigit():
        t, chats[message.chat.id].langs = translator_tools.get_langs_from_numbers([int(n) for n in txt.split()])

        # if len(t) < 2:
        #     bot.reply_to(message, "No sense to choose only 1 language. Select more",parse_mode='Markdown')
        #     return

        lgs = '+'.join([str(i) for i in t])
        #chats[message.chat.id].present = f"Your current langlist is {lgs}"
        bot.send_message(message.chat.id, f"Good! Your language list is {lgs}. Now *try to send any message*", parse_mode="Markdown")
        return

    if txt == show_it:
        start_message(message)
    elif txt == want_choose:
        choice(message)
    elif txt == want_delete:
        chats[message.chat.id].correct_used()
    elif txt == go_to_english:
        chats[message.chat.id].to_english()
        bot.send_message(message.chat.id, 'Now you are using only english')
    else:
        k = chats[message.chat.id].get_count_of_langs()
        res = translator_tools.log_text(txt, chats[message.chat.id].langs)
        chats[message.chat.id].increment_used()

        if chats[message.chat.id].get_count_of_langs() - k:
            bot.send_message(message.chat.id, '\n'.join(res), reply_markup=keyboard2, parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, '\n'.join(res), parse_mode='Markdown')



bot.polling()





if DEPLOY:
    
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
    if DEPLOY:
        server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
