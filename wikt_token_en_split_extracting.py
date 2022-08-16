# reading a single en_N.csv and process it 
# en_N.csv hold rows of token data that <= 1k data 
# each token need to process and extract metadata from Merriam Webster using this function 
# MongoDB connection is required to ensure minimum redundancy occur

import json 
import requests
import mongodb_con as db_con
import pandas as pd
import os 

api_key = "9fc0a2f9-0a05-4ee1-b1e6-f916103d108c"
search_term = ""
save_path = "/home/pc6/Desktop/merriam webster api parser/wikt_token_json"


# extract meta data from single json variable 
def extracting_norm_mw_single(clean_word):
    token_str = ""
    context_list_of_dict = []

    first_context = clean_word[0]
    token_word = first_context["meta"]["id"] 
    # token_word = re.sub('[^A-Za-z0-9]+', '', token_word)
    token_word = ''.join(filter(str.isalpha, token_word)) 
    token_str = token_word
    
    count=0
    for one_context in clean_word:
        count+=1
        # variable per context needed to write to MongoDB 
        text_compilation  = []
        visual_compilation = []

        # check dict format
        if type(one_context)== dict:
            first_layer_key = list(one_context.keys())

            if "meta" in first_layer_key:
                cuurent_text = one_context["meta"]["id"]
                current_stems = one_context["meta"]["stems"]
                current_offensive_s = one_context["meta"]["offensive"]

            if "fl" in first_layer_key:
                current_fl = one_context["fl"]
            else: 
                current_fl = "unidentified"


            if "def" in first_layer_key:
                current_def = one_context["def"][0]["sseq"]

                if isinstance(current_def, dict):
                    print("debug - dict type")
                    print(len(current_def))
                    print(current_def.keys())

                elif isinstance(current_def, list):   
                    for sense in current_def:
                        for sub_sense in sense:
                            if isinstance(sub_sense, dict):
                                print("debug - dict type")
                                print(len(sub_sense))
                                print(sub_sense.keys())

                            elif isinstance(sub_sense, list):
                                if sub_sense[0] == "pseq":                      
                                    pseq_element = sub_sense[1]
                                    if isinstance(pseq_element, list):

                                        for element in pseq_element:
                                            if element[0] == "sense":
                                                element_item = element[1]
                                                if isinstance(element_item, dict):
                                                    dt_value = element_item["dt"]

                                                    for item in dt_value:
                                                        if item[0] == "text":
                                                            text_value = item[1]
                                                            text_compilation.append(str(text_value))
                                                            if isinstance(text_value, list):
                                                                print("debug - list of text found")
                                                            elif isinstance(text_value, dict):
                                                                print("debug - dict of text found")

                                                        elif item[0] == "vis":
                                                            visual_value = item[1]
                                                            if isinstance(visual_value, list):
                                                                for visual_text in visual_value:
                                                                    if isinstance(visual_text,dict):
                                                                        single_visual_text = visual_text["t"]
                                                                        visual_compilation.append(str(single_visual_text))
                                                            elif isinstance(visual_value, dict):
                                                                print("debug - visual value dict")


                                if sub_sense[0] == "sense":
                                    element = sub_sense[1]
                                    if isinstance(element, dict):
                                        dt_value = element["dt"]
                                        for item in dt_value:
                                            if item[0] == "text":
                                                text_value = item[1]
                                                text_compilation.append(str(text_value))
                                                if isinstance(text_value, list):
                                                    print("debug - list of text found")
                                                elif isinstance(text_value, dict):
                                                    print("debug - dict of text found")

                                            elif item[0] == "vis":
                                                visual_value = item[1]
                                                if isinstance(visual_value, list):
                                                    for visual_text in visual_value:
                                                        if isinstance(visual_text,dict):
                                                            single_visual_text = visual_text["t"]
                                                            visual_compilation.append(str(single_visual_text))
                                                elif isinstance(visual_value, dict):
                                                    print("debug - visual value dict")

                                    elif isinstance(element, list):
                                        print("debug - list type")
                                        print(len(element))
                                    else:
                                        print("debug - some other type")
        else:
            print("Exception")
            
        single_context = {"context_no":count,"language":"en","pos_tag":current_fl,"offensive":current_offensive_s,"stems":current_stems,"sentence_usage":visual_compilation,"sense":text_compilation,"word_source":"MW", "remark":"winnie testing 123"}
        context_list_of_dict.append(single_context)
   
    # inserting into db 
    db_con.insert_mwdata_multiple_contexts(token_str, context_list_of_dict, remarks="inserting 1 json testing/debugging stage - wyxl")


    # check if the word exist in oov, if yes remove 
    oov_existence = db_con.check_oov(token_str)
    if oov_existence!=0: 
        # remove it as oov cause it is find it somewhere
        db_con.remove_non_oov(token_str)
    
    print("DONE")


# extract meta data from single json variable 
def extracting_norm_mw_context(clean_word):
    token_str = ""

    first_context = clean_word[0]
    token_word = first_context["meta"]["id"] 
    # token_word = re.sub('[^A-Za-z0-9]+', '', token_word)
    token_word = ''.join(filter(str.isalpha, token_word)) 
    token_str = token_word
    
    # get the latest count from mongodb
    count= db_con.find_countext_count(token_str)
    
    for one_context in clean_word:
        # variable per context needed to write to MongoDB 
        text_compilation  = []
        visual_compilation = []

        # check dict format
        if type(one_context)== dict:
            first_layer_key = list(one_context.keys())

            if "meta" in first_layer_key:
                cuurent_text = one_context["meta"]["id"]
                current_stems = one_context["meta"]["stems"]
                current_offensive_s = one_context["meta"]["offensive"]

            if "fl" in first_layer_key:
                current_fl = one_context["fl"]
            else: 
                current_fl = "unidentified"


            if "def" in first_layer_key:
                current_def = one_context["def"][0]["sseq"]

                if isinstance(current_def, dict):
                    print("debug - dict type")
                    print(len(current_def))
                    print(current_def.keys())

                elif isinstance(current_def, list):   
                    for sense in current_def:
                        for sub_sense in sense:
                            if isinstance(sub_sense, dict):
                                print("debug - dict type")
                                print(len(sub_sense))
                                print(sub_sense.keys())

                            elif isinstance(sub_sense, list):
                                if sub_sense[0] == "pseq":                      
                                    pseq_element = sub_sense[1]
                                    if isinstance(pseq_element, list):

                                        for element in pseq_element:
                                            if element[0] == "sense":
                                                element_item = element[1]
                                                if isinstance(element_item, dict):
                                                    dt_value = element_item["dt"]

                                                    for item in dt_value:
                                                        if item[0] == "text":
                                                            text_value = item[1]
                                                            text_compilation.append(str(text_value))
                                                            if isinstance(text_value, list):
                                                                print("debug - list of text found")
                                                            elif isinstance(text_value, dict):
                                                                print("debug - dict of text found")

                                                        elif item[0] == "vis":
                                                            visual_value = item[1]
                                                            if isinstance(visual_value, list):
                                                                for visual_text in visual_value:
                                                                    if isinstance(visual_text,dict):
                                                                        single_visual_text = visual_text["t"]
                                                                        visual_compilation.append(str(single_visual_text))
                                                            elif isinstance(visual_value, dict):
                                                                print("debug - visual value dict")

                                if sub_sense[0] == "sense":
                                    element = sub_sense[1]
                                    if isinstance(element, dict):
                                        dt_value = element["dt"]
                                        for item in dt_value:
                                            if item[0] == "text":
                                                text_value = item[1]
                                                text_compilation.append(str(text_value))
                                                if isinstance(text_value, list):
                                                    print("debug - list of text found")
                                                elif isinstance(text_value, dict):
                                                    print("debug - dict of text found")

                                            elif item[0] == "vis":
                                                visual_value = item[1]
                                                if isinstance(visual_value, list):
                                                    for visual_text in visual_value:
                                                        if isinstance(visual_text,dict):
                                                            single_visual_text = visual_text["t"]
                                                            visual_compilation.append(str(single_visual_text))
                                                elif isinstance(visual_value, dict):
                                                    print("debug - visual value dict")

                                    elif isinstance(element, list):
                                        print("debug - list type")
                                        print(len(element))
                                    else:
                                        print("debug - some other type")
        
            # insert single context
            single_context = {"context_no":count,"language":"en","pos_tag":current_fl,"offensive":current_offensive_s,"stems":current_stems,"sentence_usage":visual_compilation,"sense":text_compilation,"word_source":"MW", "remark":"winnie testing 123"}
            db_con.update_context_MW(db_con.mongo_token(), token_str, single_context)
            count +=1
        else:
            print("Exception")
    print("DONE")


# pass in en file number 
# such as en_0.csv, pass in en_file_no = 0
# some logic for token and oov (consider about possible scenarios)
# if token table got the insert into token, if second source then add context only 
# if oov table got, but the word metadata exist in lexicon source, remove from oov and add into token
# if token table got, but other lexicon source show None, stick back to the token table, not classify as OOV
def mw_system(en_file_no=1):
    df = pd.read_csv('wikt_token_en_split/en_'+ str(en_file_no) +'.csv')
    en_list = df.text.tolist()
    count = 0
    if len(en_list)<=1000:
        for i in en_list:
            count+=1
            print(count, ' ->', i)

            # check from oov? 

            # check from melex 
            if db_con.check_token(i)==1:
                # token exist in melex
                # check whether MW exist 
                # check any source of "wn" inside context
                wn_source_check = db_con.mongo_token().find({"token":i, "contexts.word_source": "MW" })
                wn_source_check = list(wn_source_check)
                if len(wn_source_check) == 0:
                    # the word does exist for other lexicon but not merriam webster
                    # get the search term, get the matadata from MW api 
                    search_term = i
                    req = requests.get(f"https://www.dictionaryapi.com/api/v3/references/collegiate/json/{search_term}?key={api_key}")
                    data = req.json()

                    if(type(data[0]) is dict):
                        with open(save_path + '/'+ search_term+ '.json', 'w') as f:
                            json.dump(data, f)
                        # with open(f'{search_term}.json', 'w') as f:
                        #     json.dump(data, f)
                        extracting_norm_mw_context(data)
                        print('Yes' )
                        print("debug n validating ->", i)
                    else:
                        print('Not found in merriam webster -' + i)
                
                else: 
                    # the word of crawled from merriam webster somehow repeated
                    print("debug - warning - duplication") 
     
            else:
                # token does not exist in melex 
                # add a new record/row into the table

                search_term = i
                req = requests.get(f"https://www.dictionaryapi.com/api/v3/references/collegiate/json/{search_term}?key={api_key}")
                data = req.json()
                if len(data)==0:
                    # nothing return from api
                    # it might due to nothing found 
                    db_con.insert_single_oov(i, remark="test run on first wikt file")

                elif(type(data[0]) is dict):
                    # there is something return from the MW API
                    db_con.insert_api_found_term(i, remark = "test run on first wikt file")
                    with open(save_path + '/'+ search_term+ '.json', 'w') as f:
                        json.dump(data, f)
                        
                    # here do the single token insertion
                    extracting_norm_mw_single(data)
                    print("debug n validating ->", i)

                else:
                    db_con.insert_single_oov(i, remark="test run on first wikt file")
                     
    print("COMPLETED")










# Option1: either read a complete directory and process it - extracting_norm_mw_directory()
# Option2: either straight process right after it is being stored in json - extracting_norm_mw_single(clean_word)

# Option 1 #####################################################################################################

def extracting_norm_mw_directory():
    # get all the file from directory 
    files = os.listdir("/home/pc6/Desktop/merriam webster api parser/wikt_token_json")
    path = "/home/pc6/Desktop/merriam webster api parser/wikt_token_json/"
    for each_file in files:
        f = open(path + each_file)
        clean_word = json.load(f)
        f.close()

        token_str = ""
        context_list_of_dict = []

        first_context = clean_word[0]
        token_word = first_context["meta"]["id"] 
        # token_word = re.sub('[^A-Za-z0-9]+', '', token_word)
        token_word = ''.join(filter(str.isalpha, token_word)) 
        token_str = token_word

        #  here need to check db
        if db_con.check_token(token_str)==0:
            count=0
            for one_context in clean_word:
                count+=1
                # variable per context needed to write to MongoDB 
                text_compilation  = []
                visual_compilation = []

                # check dict format
                if type(one_context)== dict:
                    first_layer_key = list(one_context.keys())

                    if "meta" in first_layer_key:
                        cuurent_text = one_context["meta"]["id"]
                        current_stems = one_context["meta"]["stems"]
                        current_offensive_s = one_context["meta"]["offensive"]

                    if "fl" in first_layer_key:
                        current_fl = one_context["fl"]

                    if "def" in first_layer_key:
                        current_def = one_context["def"][0]["sseq"]

                        if isinstance(current_def, dict):
                            print("debug - dict type")
                            print(len(current_def))
                            print(current_def.keys())

                        elif isinstance(current_def, list):   
                            for sense in current_def:
                                for sub_sense in sense:
                                    if isinstance(sub_sense, dict):
                                        print("debug - dict type")
                                        print(len(sub_sense))
                                        print(sub_sense.keys())

                                    elif isinstance(sub_sense, list):
                                        if sub_sense[0] == "pseq":                      
                                            pseq_element = sub_sense[1]
                                            if isinstance(pseq_element, list):

                                                for element in pseq_element:
                                                    if element[0] == "sense":
                                                        element_item = element[1]
                                                        if isinstance(element_item, dict):
                                                            dt_value = element_item["dt"]

                                                            for item in dt_value:
                                                                if item[0] == "text":
                                                                    text_value = item[1]
                                                                    text_compilation.append(str(text_value))
                                                                    if isinstance(text_value, list):
                                                                        print("debug - list of text found")
                                                                    elif isinstance(text_value, dict):
                                                                        print("debug - dict of text found")

                                                                elif item[0] == "vis":
                                                                    visual_value = item[1]
                                                                    if isinstance(visual_value, list):
                                                                        for visual_text in visual_value:
                                                                            if isinstance(visual_text,dict):
                                                                                single_visual_text = visual_text["t"]
                                                                                visual_compilation.append(str(single_visual_text))
                                                                    elif isinstance(visual_value, dict):
                                                                        print("debug - visual value dict")


                                        if sub_sense[0] == "sense":
                                            element = sub_sense[1]
                                            if isinstance(element, dict):
                                                dt_value = element["dt"]
                                                for item in dt_value:
                                                    if item[0] == "text":
                                                        text_value = item[1]
                                                        text_compilation.append(str(text_value))
                                                        if isinstance(text_value, list):
                                                            print("debug - list of text found")
                                                        elif isinstance(text_value, dict):
                                                            print("debug - dict of text found")

                                                    elif item[0] == "vis":
                                                        visual_value = item[1]
                                                        if isinstance(visual_value, list):
                                                            for visual_text in visual_value:
                                                                if isinstance(visual_text,dict):
                                                                    single_visual_text = visual_text["t"]
                                                                    visual_compilation.append(str(single_visual_text))
                                                        elif isinstance(visual_value, dict):
                                                            print("debug - visual value dict")

                                            elif isinstance(element, list):
                                                print("debug - list type")
                                                print(len(element))
                                            else:
                                                print("debug - some other type")

                else:
                    print("Exception")
                    
                single_context = {"context_no":count,"language":"en","pos_tag":current_fl,"offensive":current_offensive_s,"stems":current_stems,"sentence_usage":visual_compilation,"sense":text_compilation,"word_source":"MW", "remark":"winnie testing 123"}
                context_list_of_dict.append(single_context)
            print(token_str)
            # inserting into db 
            db_con.insert_mwdata_multiple_contexts(token_str, context_list_of_dict, remarks="testing/debugging stage - wyxl")
        else:
            db_con.insert_melex_dup_term(token_str, "duplicate during json extraction")
    print("DONE")
