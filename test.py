
import translator_tools
from translator_tools import smart_to_tidy
import recognition_tools
import random

import telebot

#import requests
#from pydub import AudioSegment
#import soundfile as sf
from flask import Flask, request
import os

API_TOKEN = '1059809966:AAHfjWbOyF3h-F_UZi6krWylOHvA7W3SGE4'

bot = telebot.TeleBot(API_TOKEN)
# server = Flask(__name__)
# PORT = int(os.environ.get('PORT', '8443'))



instructions = """Hello! I'm the translator bot!

I will translate your messages into all chosen languages. After u can reply my answers to your foreign friends!

Also u can reply messages here.

All u need is to choose necessary languages and start messaging!


WARNING: because of free deploy your settings are reset periodically. If u haven't got a translate in 10sec, don't worry, just choose languages again. Fortunately, if u will send message into language not from langlist, this one is added automatically.

Problems? Questions? Write an issue https://github.com/PasaOpasen/TranslatorBot"""

show_it = 'Show instructions again, bot!'
want_choose = 'Choose languages'
set_audio = 'Set audio lang, bot'
show_settings = 'Show my settings'
second_keyboard = False

my_langs = ['ru','en']
audio_lang = 'en'

present = "U haven't selected languages yet (default Russian+English)"

def SendMessage1(id, text):
    global second_keyboard
    if second_keyboard:
        bot.send_message(id, text, reply_markup=keyboard1)
        second_keyboard = False
    else:
        bot.send_message(id, text)


keyboard1 = telebot.types.ReplyKeyboardMarkup(True,True, row_width=2)
keyboard1.row(show_it, want_choose)
keyboard1.add(set_audio,show_settings)
#keyboard1.add(show_settings)


def choice(id):
    mes = ['Supported languages:\n']
    mes.extend([f'{n+1}. {lang}' for n, lang in enumerate(translator_tools.all_langs)])
    inds = [76, 22, 71]     #[random.randint(1,100), random.randint(1,100), random.randint(1,100)]
    a, _ = translator_tools.get_langs_from_numbers(inds)
    mes.append(f"""\nU should choose some languages' numbers and write them like '1 2 3' (without quotes).

For example, the answer '{" ".join([str(i) for i in inds])}' means {"+".join(a)}.

{present}""")

    #bot.send_message(id, '\n'.join(mes))
    SendMessage1(id,'\n'.join(mes))

def choice_audio(id):
    global second_keyboard
    mes = ['Supported languages:\n']
    mes.extend([f'{n+1}. {lang}' for n, lang in enumerate(translator_tools.all_langs)])
    mes.append("""\nIn order to set the language of audio (default is English) u should write the number of this language""")

    keyboard2 = telebot.types.ReplyKeyboardMarkup(True)
    keyboard2.row(*smart_to_tidy(my_langs))
    bot.send_message(id, '\n'.join(mes), reply_markup=keyboard2)
    second_keyboard = True

def show_my_settings(id):
    mes = [f"Langlist = {'+'.join(smart_to_tidy(my_langs))}",f"Audio lang = {translator_tools.lang_dic_reversed[audio_lang]}"]
    #bot.send_message(id, '\n'.join(mes), reply_markup=keyboard1)
    SendMessage1(id, '\n'.join(mes))

@bot.message_handler(commands=['start', 'help'])
def start_message(message):
    bot.send_message(message.chat.id, instructions, reply_markup=keyboard1)

@bot.message_handler(content_types=['voice'])
def get_from_voicy(message):
    bot.send_message('@voicybot','/start')
    bot.send_message('@voicybot', '/language')
    bot.send_message('@voicybot', 'English')
    bot.send_voice('@voicybot', message.voice)


# def prepare_audio(message):
#
#     file_info = bot.get_file(message.voice.file_id)
#
#     downloaded_file = bot.download_file(file_info.file_path)
#
#     bot.send_message(message.chat.id, 1)
#
#     name = f'{message.chat.id}'
#     with open(f'{name}.ogg', 'wb') as new_file:
#         new_file.write(downloaded_file)
#
#     bot.send_message(message.chat.id, 2)
#
#     #data, samplerate = sf.read(f'{name}.ogg')
#     #sf.write(f'{name}.wav', data, samplerate)
#     AudioSegment.from_ogg(f'{name}.ogg').export(f'{name}.wav', format="mp3")
#
#     bot.send_message(message.chat.id, 3)
#
#     success, text = recognition_tools.speech_to_text_from_wav(audio_lang, f'{name}.wav')
#
#     bot.send_message(message.chat.id, text)


@bot.message_handler(content_types=['text'])
def send_text(message):
    global audio_lang

    txt = message.text.strip()
    if txt[0].isdigit() and txt[-1].isdigit():
        global my_langs, present

        t, langs = translator_tools.get_langs_from_numbers([int(n) for n in txt.split()])

        if len(t) == 1:
            bot.reply_to(message, f"I see only one language: {t[0]}. It's the expected language of audio messages", reply_markup=keyboard1)
            audio_lang = langs[0]
            return

        my_langs = langs

        lgs = '+'.join([str(i) for i in t])
        present = f"Your current langlist is {lgs}"
        #bot.send_message(message.chat.id,f"Good! Your langlist is {lgs}. Now try to send any message", reply_markup=keyboard1)
        SendMessage1(message.chat.id,f"Good! Your langlist is {lgs}. Now try to send any message")
        return

    if txt == show_it:
        start_message(message)
    elif txt == want_choose:
        choice(message.chat.id)
    elif txt == set_audio:
        choice_audio(message.chat.id)
    elif txt == show_settings:
        show_my_settings(message.chat.id)
    elif txt in smart_to_tidy(my_langs):
        audio_lang = translator_tools.lang_dic[txt]
        #bot.send_message(message.chat.id, f'Okay, your audio lang is {txt}', reply_markup=keyboard1)
        SendMessage1(message.chat.id, f'Okay, your audio lang is {txt}')
    else:
        res = translator_tools.log_text(txt, my_langs)
        #bot.send_message(message.chat.id, '\n'.join(res), reply_markup=keyboard1)
        SendMessage1(message.chat.id, '\n'.join(res))


def listener(messages):
    for m in messages:
        print(str(m))


bot.set_update_listener(listener)

bot.polling()


# @server.route('/' + API_TOKEN, methods=['POST'])
# def getMessage():
#     bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
#     return "!", 200
#
#
# @server.route("/")
# def webhook():
#     bot.remove_webhook()
#     bot.set_webhook(url='https://multi-translator-bot.herokuapp.com/' + API_TOKEN)
#     return "!", 200
#
#
# if __name__ == "__main__":
#     server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))


#Ctrl+/