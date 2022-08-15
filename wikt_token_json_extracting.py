import mongodb_con as db_con 
import json 
import os

# Option1: either read a complete directory and process it - extracting_norm_mw_directory()
# Option2: either straight process right after it is being stored in json - extracting_norm_mw_single(clean_word)

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

def extracting_norm_mw_single(clean_word):
    token_str = ""
    context_list_of_dict = []

    first_context = clean_word[0]
    token_word = first_context["meta"]["id"] 
    # token_word = re.sub('[^A-Za-z0-9]+', '', token_word)
    token_word = ''.join(filter(str.isalpha, token_word)) 
    token_str = token_word

    #  here need to insert another condition chcking 

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
   
    # inserting into db 
    db_con.insert_mwdata_multiple_contexts(token_str, context_list_of_dict, remarks="inserting 1 json testing/debugging stage - wyxl")
    print("DONE")
