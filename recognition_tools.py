# -*- coding: utf-8 -*-
"""
Created on Wed Jun  3 11:53:36 2020

@author: qtckp
"""


import speech_recognition as sr

bad_result_message = 'Cannot understand, try to say again'

def speech_to_text_from_wav(lang = 'ru', file = 'tmp.wav'):

    # Initialize recognizer class (for recognizing the speech)
    r = sr.Recognizer()
    
    # Reading Audio file as source
    # listening the audio file and store in audio_text variable
    
    with sr.AudioFile(file) as source:
        
        audio_text = r.listen(source)
        
    # recoginize_() method will throw a request error if the API is unreachable, hence using exception handling
        try:
            return True, r.recognize_google(audio_text, language = lang)
        except Exception:
            return False, bad_result_message
             

     








