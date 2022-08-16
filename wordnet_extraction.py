import nltk
nltk.download('wordnet')
nltk.download('omw-1.4')
from nltk.corpus import wordnet as wn
import pandas as pd
import mongodb_con as db_con 

def wordnet_retrieve_data(token, remarks="testing on WN insertion -1"):
    possible_tag = []
    possible_synsets = []
    possible_definition = []
    possible_examples = []
    synonyms = []
    antonyms = []
    syns = wn.synsets(token) 
    
    for post in syns:
        frame = post.pos()
        frame_name = post.name()
        frame_definition = post.definition()
        frame_examples = post.examples()
        for l in post.lemmas():
            synonyms.append(l.name())
            if l.antonyms():
                antonyms.append(l.antonyms()[0].name())

        possible_tag.append(frame)
        possible_synsets.append(frame_name)
        possible_definition.append(frame_definition)
        possible_examples.append(frame_examples)
    
    tags = []
    for item in possible_tag: 
        if item == "a" or item =="s":
            tags.append("ADJ")
        elif item == "n":
            tags.append("NOUN")
        elif item == "v":
            tags.append("VERB")
        elif item == "r":
            tags.append("ADV")
    
    if len(tags)==0 and len(possible_synsets)==0 and len(possible_definition)==0 and len(possible_examples)==0 and len(synonyms)==0 and len(antonyms)==0:
        
        
        # insert into OOV table 
        # check condition before inserting too 

        # before inserting into oov, check if this word exist in melex before 
        # if yes, then there is no need to insert into oov 
        if db_con.check_token(token)==0: # not a token before, might be oov 
            if db_con.check_oov(token)==0: # not a recorded oov before 
                db_con.insert_single_oov(token, remark=remarks)
            else: 
                print("duplicated OOV found")
        else: 
            # as a token before, 100% not oov 
            # dont add into oov 
            print("not oov although not identified in wordnet")

        # # but what if this word is registered into melex token table? 
        # if db_con.check_token(token)==1:
        #     print("some weird thing happen hehe :)")
            
        return "OOV"

    else: 

        # the word is not oov in wordnet

        context_list_of_dict = []
        # check token exist before or not 
        # condition 4: https://docs.google.com/spreadsheets/d/1hzpRjnvbDRuu0NI0NDP-nm-F1iJIJATXfnKOqaPusaw/edit#gid=1882015912 
        # check from melex 
        if db_con.check_token(token)==0:
            # token does not exist in melex 
            # prepare multiple context possibility 
            # insert into token table 
            
            contexts_available = len(tags)
            count=0
            if contexts_available>1:
                for i in range(contexts_available):
                    count+=1
                    current_tag = tags[i]
                    print(current_tag)
                    current_synset = possible_synsets[i]
                    print(current_synset)
                    current_definition = possible_definition[i]
                    print(current_definition)
                    current_example = possible_examples[i]
                    print(current_example)
                    current_synonym = synonyms
                    print(current_synonym)
                    current_anonym = antonyms
                    print(current_anonym)
                    print("\n")

                    single_context = {"context_no":count,"language":"en", "pos_tag":current_tag, "synsets":current_synset,"definition":current_definition, "sentence_usage":current_example,"synonyms":synonyms,"antonyms":antonyms,"word_source":"WN", "remark":remarks}
                    context_list_of_dict.append(single_context)

                db_con.insert_wndata(token,context_list_of_dict)
            
                # after insertion, check if ths word exist in oov, yes then remove 
                # check if the word exist in oov, if yes remove 
                oov_existence = db_con.check_oov(token)
                if oov_existence!=0:
                    # remove it as oov cause it is find it somewhere in other lexicon source 
                    db_con.remove_non_oov(token)

        else:
            # condition 1
            # token exist in melex
            # might due to duplication OR 
            # might due to never insert other source of lexicon before 
            # how to check whether 
            
            # check any source of "wn" inside context
            wn_source_check = db_con.mongo_token().find({"token":token, "contexts.word_source": "WN" })
            wn_source_check = list(wn_source_check)
            if len(wn_source_check) == 0:
                
                # need to use update_one 
                # URGHH INI HARD OHH 
                contexts_available = len(tags)
                count = db_con.find_countext_count(token)
                for i in range(contexts_available):
                    current_tag = tags[i]
                    print(current_tag)
                    current_synset = possible_synsets[i]
                    print(current_synset)
                    current_definition = possible_definition[i]
                    print(current_definition)
                    current_example = possible_examples[i]
                    print(current_example)
                    current_synonym = synonyms
                    print(current_synonym)
                    current_anonym = antonyms
                    print(current_anonym)
                    print("\n")

                    single_context = {"context_no":count,"language":"en", "pos_tag":current_tag, "synsets":current_synset,"definition":current_definition, "sentence_usage":current_example,"synonyms":synonyms,"antonyms":antonyms,"word_source":"WN", "remark":remarks}
                    db_con.update_context_WN(db_con.mongo_token(), token, single_context)
                    count+=1
                
            # else:
            #     db_con.insert_melex_dup_term(token, "duplicate during WN extraction")

        return "TOKEN",context_list_of_dict


import json 
import requests
import os

def wn_system(number=1):
    df = pd.read_csv('wikt_token_en_split/en_'+ str(number) +'.csv')
    en_list = df.text.tolist()
    # print(type(en_list))
    output_list = list(map(wordnet_retrieve_data, en_list))
    return output_list

