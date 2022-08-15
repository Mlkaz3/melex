# reading a single en_N.csv and process it 
# en_N.csv hold rows of token data that <= 1k data 
# each token need to process and extract metadata from Merriam Webster using this function 
# MongoDB connection is required to ensure minimum redundancy occur

import json 
import requests
import os
import mongodb_con as db_con
import pandas as pd


default_api_key = "9fc0a2f9-0a05-4ee1-b1e6-f916103d108c"
default_search_term = ""

# log/record tracing
melex_dup_term = []
oov_dup_term = []
api_found_term = []
api_not_found_term = []

save_path = "/home/pc6/Documents/merriam webster api parser/wikt_token_json"



def create_file():
    save_path = "/home/pc6/Documents/merriam webster api parser/log_record_tracing"
    file_exists = os.path.exists(save_path+'/api_found_term.csv')
    if not file_exists:
        file = open(save_path+'api_found_term.csv','x')
    
    file_exists = os.path.exists(save_path+'/api_not_found_term.csv')
    if not file_exists:
        file = open(save_path+'api_not_found_term.csv','x')
    
    file_exists = os.path.exists(save_path+'/oov_dup_term.csv')
    if not file_exists:
        file = open(save_path+'oov_dup_term.csv','x')
    
    file_exists = os.path.exists(save_path+'/melex_dup_term.csv')
    if not file_exists:
        file = open(save_path+'melex_dup_term.csv','x')
    

# to store melex and oov inserted word into a df 
# besides any redundancy has occured into another file 
def log_record_tracing(api_found_term,api_not_found_term,oov_dup_term,melex_dup_term):
    
    create_file()
    
    # read all 4 files in 
    api_found_term_df = pd.read_csv('api_found_term.csv')
    api_not_found_term_df = pd.read_csv('api_not_found_term.csv')
    oov_dup_term_df = pd.read_csv('oov_dup_term.csv')
    melex_dup_term_df = pd.read_csv('melex_dup_term.csv')
    
    # convert them to list 
    # check condition of null 
    api_found_term_ls = []
    api_not_found_term_ls = []
    oov_dup_term_ls = []
    melex_dup_term_ls = []

    if not api_found_term_df.empty:
        api_found_term_ls = api_found_term_df.text.tolist()
        api_not_found_term_ls = api_not_found_term_df.text.tolist()
        oov_dup_term_ls = oov_dup_term_df.text.tolist()
        melex_dup_term_ls = melex_dup_term_df.text.tolist()
    
    # append the list all together 
    api_found_term_ls.append(api_found_term)
    api_not_found_term_ls.append(api_not_found_term)
    oov_dup_term_ls.append(oov_dup_term)
    melex_dup_term_ls.append(melex_dup_term)
    
    # write updated version to 4 files 
    api_found_term_ls.to_csv('api_found_term.csv', header='text')
    api_not_found_term_ls.to_csv('api_not_found_term.csv', header='text')
    oov_dup_term_ls.to_csv('oov_dup_term.csv', header='text')
    melex_dup_term_ls.to_csv('melex_dup_term.csv', header='text')
    
log_record_tracing([],[],[],[])

# pass in en file number 
# such as en_0.csv, pass in en_file_no = 0
def mw_system(en_file_no):
    df = pd.read_csv('wikt_token_en_split/en_'+ str(en_file_no) +'.csv')
    en_list = df.text.tolist()
    count = 0
    if len(en_list)<=1000:
        for i in en_list:
            count+=1
            print(count, ' ->', i)
            #check from melex 
            if db_con.check_token(i)==0:
                #token does not exist in melex 
                #check from oov 
                if db_con.check_oov(i)==0:
                    #token does not exist in melex 
                    #check lexicalized status using api key
                    #SOON: proposing a better method to not waste api key
                    search_term = i
                    req = requests.get(f"https://www.dictionaryapi.com/api/v3/references/collegiate/json/{search_term}?key={api_key}")
                    data = req.json()
                    if len(data)==0:
                        api_not_found_term.append(i)
                        # add into oov database
                        db_con.insert_single_oov(i, remark="test run on first wikt file")
                    elif(type(data[0]) is dict):
                        api_found_term.append(i)
                        with open(f'{save_path,search_term}.json', 'w') as f:
                            json.dump(data, f)
                    else:
                        api_not_found_term.append(i)
                        # add into oov database
                        db_con.insert_single_oov(i, remark="test run on first wikt file")
                else:
                    oov_dup_term.append(i)
            else:
                melex_dup_term.append(i)
    
    log_record_tracing(api_found_term,api_not_found_term,oov_dup_term,melex_dup_term)

