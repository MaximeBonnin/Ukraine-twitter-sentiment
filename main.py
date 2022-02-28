from pydoc import text
from API_KEYS import *

import requests
import nltk
import pandas as pd
import string
from deep_translator import GoogleTranslator


term1 = "%D0%A3%D0%BA%D1%80%D0%B0%D0%B8%D0%BD%D0%B0" # "украина" = Ukraine in russian   
term2 = "%D0%A0%D0%BE%D1%81%D1%81%D0%B8%D1%8F" # = "Россия" Russia in russian
#term = "ukraine"
lang = "ru"
#lang = "en"


def get_tweets(term1, term2, lang):
    headers = {'Authorization': f'Bearer {BEARER_TOKEN}'}
    base_url = "https://api.twitter.com/1.1/search/tweets.json"
    # url = f"{base_url}?q={term}&q=lang%3A{lang}&count=100"
    url = f"{base_url}?q={term1}%20{term2}&q=lang%3A{lang}&count=100"

    r = requests.get(url, headers=headers)
    return r.json()


def get_text(response_dict):
    tweet_list = []
    for r in response_dict["statuses"]:
        tweet_list.append(r["text"])

    return tweet_list


def clean(tweet_list, language):

    # remove stopwords and punctuatiopn
    stopwords = nltk.corpus.stopwords.words(language)
    stopwords.extend(string.punctuation)
    stopwords.extend(["https"])

    output = []
    for tweet in tweet_list:
        words = nltk.word_tokenize(tweet.lower())
        cleaned = [word for word in words if (word not in stopwords) and len(word) > 2 and word.isalnum()]
        clean_tweet = " ".join(cleaned)
        output.append(clean_tweet)
    
    return output


def make_table(txt):
    clean_tweet_list = txt

    clean_wl = []
    for tweet in clean_tweet_list:
        for word in tweet.split(" "):
            clean_wl.append(word)
        
    
    wl_set = list(set(clean_wl))
    count_list = []
    for w in wl_set:
        count_list.append(clean_wl.count(w))
    
    data = {"count": count_list, "word": wl_set}
    df = pd.DataFrame(data)
    df.dropna()
    return df.sort_values("count", ascending=False, ignore_index=True)


def add_translation(clean_txt, df):
    # THIS IS NOT a 1:1 translation of the words. The entire tweets are translated and then the words are counted.
    text_chunk = ""
    translated_tweets = []
    for tweet in clean_txt:
        if len(text_chunk) + len(tweet) >= 2500:
            translated_chunk = GoogleTranslator(source="auto", target="en").translate(text_chunk)
            translated_tweets.extend(clean(translated_chunk.split("."), "english"))
            text_chunk = tweet
        else:
            text_chunk = f"{text_chunk} {tweet}"

    df_t = make_table(translated_tweets)

    combined_df = pd.concat([df, df_t], axis=1, ignore_index=True, sort=True)
    combined_df.columns = ["count", "word","count_en","word_en"]
    combined_df["count"] = combined_df["count"].fillna(0)
    combined_df["count_en"] = combined_df["count_en"].fillna(0)
    combined_df["count_en"] = combined_df["count_en"].astype(int)

    return combined_df


def main():
    response_dict = get_tweets(term1, term2, lang)
    txt = get_text(response_dict)
    clean_txt = clean(txt, "russian")
    df = make_table(clean_txt)
    df_with_translation = add_translation(clean_txt, df)
    print(df_with_translation.head(25))


if __name__ == "__main__":
    main()