from ast import Pass
from itertools import count
from tkinter import W
from matplotlib.pyplot import text
from pandas import concat
import requests
from pprint import pprint
from API_KEYS import *
import numpy as np
import pandas as pd
from googletrans import Translator



search_url = "https://twitter.com/search?q=%D0%A3%D0%BA%D1%80%D0%B0%D0%B8%D0%BD%D0%B0&src=typed_query&f=top" 
api_part = "?q=%D0%A3%D0%BA%D1%80%D0%B0%D0%B8%D0%BD%D0%B0&src=typed_query&f=top"
with_country = f"{api_part}&q=lang%3Aru"

term = "%D0%A3%D0%BA%D1%80%D0%B0%D0%B8%D0%BD%D0%B0"
lang = "%3Aru"

def get_tweets(term, lang):
    headers = {'Authorization': f'Bearer {BEARER_TOKEN}'}
    base_url = "https://api.twitter.com/1.1/search/tweets.json"
    url = f"{base_url}?q={term}&q=lang{lang}&count=100"

    r = requests.get(url, headers=headers)
    return r.json()


def get_text(response_dict):
    text_list = []
    for r in response_dict["statuses"]:
        text_list.append(r["text"])

    return text_list


def make_table(txt):
    one_str = " ".join(txt)
    word_list = one_str.split(" ")
    clean_wl = []
    for w in word_list:
        w = w.lower().strip()
        for sym in [",", ".", ":", "!", "\n"]:
            w = w.replace(sym, "")
        if len(w) > 0:
            clean_wl.append(w)
    
    wl_set = list(set(clean_wl))
    count_list = []
    for w in wl_set:
        count_list.append(clean_wl.count(w))
    
    data = {"count": count_list, "word": wl_set}
    df = pd.DataFrame(data)
    df.dropna()
    return df
    
    
def add_translation(df):
    try:
        t_words = []
        for w in list(df["word"]):
            translator = Translator()
            result = translator.translate(w, src='ru', dest='en')
            print(result)
            t_words.append(result)
        print(t_words)
    except AttributeError as e:
        print(f"AttributeError while translating: {e}")




def main():
    response_dict = get_tweets(term, lang)
    txt = get_text(response_dict)
    df = make_table(txt)
    add_translation(df)


if __name__ == "__main__":
    main()