# -*- coding: utf-8 -*-
"""
Created on Tue Jun  2 17:55:33 2020

@author: qtckp
"""

import googletrans
from googletrans import Translator

#from pygoogletranslation import Translator

from textblob import TextBlob

import time

#import speech_recognition as sr
#from scipy.io.wavfile import write
#import numpy as np

#import epitran
#from pysle import isletool
#from PersianG2p import Persian_g2p_converter

#import json

#from termcolor import colored
#import colorama
#colorama.init()


epis = {}

translator = Translator(service_urls = ['translate.google.com', 'translate.google.co.kr'])
#translator = Translator()

#bad_result_message = '**!!! BAD RESULT OF RECOGNITION. U CAN TRY AGAIN**'


lang_dic = {value.title(): key for key, value in googletrans.LANGUAGES.items()}
lang_dic_reversed = {key: f'*{value.capitalize()}*' for key, value in googletrans.LANGUAGES.items()}

all_langs = list(lang_dic.keys())



def from_code_to_name(language):
    return  lang_dic_reversed[language]

def smart_to_tidy(langs):
    return [lang_dic_reversed[l] for l in langs]

def get_code_from_lang(lang):
    return lang_dic[lang.tolower()]


def log_text(text, lang_list = ['en','ru']):
    
    result = []
    
    if len(text) < 3:
        result.append(f'*too shirt text*: {text}')
        return result
    

    lang_of_text = translator.detect(text).lang
    #if len(lang_of_text) == 0: lang_of_text = 'en'
    #print(lang_of_text)

    bool_list = [r != lang_of_text for r in lang_list]
    
    if all(bool_list):
        bool_list.append(False)
        lang_list.append(lang_of_text)
    
    for lang, it in zip(lang_list, bool_list):
        result.append(f'{lang_dic_reversed[lang].upper()}:')
        if it:
            time.sleep(0.7)
            #print(f"{text}, {lang}, {lang_of_text}")
            txt = translator.translate(text, dest = lang, src = lang_of_text).text
            result.append(txt)
        else:
            txt = text
            result.append(f'_(original text)_ {text}')
        result.append('')
    
    return result


def log_text_better(text, lang_list = ['en','ru']):
    
    result = []
    
    if len(text) < 3:
        result.append(f'*too shirt text*: {text}')
        return result
    
    blob = TextBlob(text)

    lang_of_text = blob.detect_language()

    bool_list = [r != lang_of_text for r in lang_list]
    
    if all(bool_list):
        bool_list.append(False)
        lang_list.append(lang_of_text)
    
    for lang, it in zip(lang_list, bool_list):
        result.append(f'{lang_dic_reversed[lang].upper()}:')
        if it:
            time.sleep(1.3)
            txt = str(blob.translate(from_lang = lang_of_text, to=lang))
            result.append(txt)
        else:
            txt = text
            result.append(f'_(original text)_ {text}')
        result.append('')
    
    return result


def get_langs_from_numbers(numbers):
    
    l1 = [all_langs[k-1] for k in numbers]
    
    return l1, [lang_dic[k] for k in l1]






if __name__ == '__main__':

    #trans = Translator()
    #print(trans.detect('Привет'))
    #print(trans.detect('Hello').lang)
    #print(trans.translate('Привет'))




   
    defs = ['en','ru']
    
    r = log_text('hello my friend',defs)
    
    print('\n'.join(r))

    r = log_text('Ich will',defs)
    
    print('\n'.join(r))
    
    print(defs)
    
    r = log_text_better('hello my friend',defs)
    
    print('\n'.join(r))

    lang = Translator().detect('Hello boy')
    print(lang)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    