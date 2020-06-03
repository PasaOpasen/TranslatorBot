# -*- coding: utf-8 -*-
"""
Created on Tue Jun  2 17:55:33 2020

@author: qtckp
"""

import googletrans
from googletrans import Translator
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
translator = Translator()
bad_result_message = '**!!! BAD RESULT OF RECOGNITION. U CAN TRY AGAIN**'


lang_dic = {value.title(): key for key, value in googletrans.LANGUAGES.items()}
lang_dic_reversed = {key: value.capitalize() for key, value in googletrans.LANGUAGES.items()}

all_langs = list(lang_dic.keys())


def get_code_from_lang(lang):
    return lang_dic[lang.tolower()]


def log_text(text, lang_list = ['en','ru']):
    
    result = []
    
    if len(text) < 3:
        result.append(f'too small text: {text}')
        return result
    

    lang_of_text = translator.detect(text).lang

    bool_list = [r != lang_of_text for r in lang_list]
    
    if all(bool_list):
        bool_list.append(False)
        lang_list.append(lang_of_text)
    
    for lang, it in zip(lang_list, bool_list):
        result.append(f'{lang_dic_reversed[lang].upper()}:')
        if it:
            txt = translator.translate(text, dest = lang, src = lang_of_text).text
            result.append(txt)
        else:
            txt = text
            result.append(f'(original text) {text}')
        result.append('')
    
    return result


def get_langs_from_numbers(numbers):
    
    l1 = [all_langs[k-1] for k in numbers]
    
    return l1, [lang_dic[k] for k in l1]






if __name__ == '__main__':
   
    defs = ['en','ru']
    
    r = log_text('hello my friend',defs)
    
    print('\n'.join(r))

    r = log_text('Ich will',defs)
    
    print('\n'.join(r))
    
    print(defs)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    