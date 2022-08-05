# to split the en file contains 387528 rows to <= 1k data within a csv 
# the split will rename in a way en_N.csv wheer N is the file naming sequence, inc by 1 
# there is a text file named log.txt within the directory to store latest sequence, read when process
# 5/8/2022 en_387.csv 

import pandas as pd 
import math
import numpy as np
import os.path

def mw_splitting(filename = "wikt_token/en.csv"):
    """
    This function aims to split the large unvalidate token into smaller chunk files.
    Each file will store a maximum of 1000 tokens only in csv file format.
    """
    df = pd.read_csv(filename)
    en_list = df.text.tolist()
    en_list_len = len(en_list)
    mm = math.ceil(en_list_len/1000) # split into <=1000 token per array 
    en_splitting = np.array_split(en_list,mm)
    

    #  to continue from where it stop, get the last count number
    # loop through the list of list 
    # should output 388 file in this case
    count=None

    file_exists = os.path.exists('wikt_token_en_split/log.txt')
    if file_exists:
        file = open('wikt_token_en_split/log.txt','r')
        file_content = file.read()
        if file_content!= "":
            print("file is not empty")
            print(file_content)
            count = int(file_content)
        else:
            print("empty")
            count=0
        file.close()
    else: 
        file = open('wikt_token_en_split/log.txt','x')
        count=0

    
    for en_l in en_splitting:
        df = pd.DataFrame(en_l)
        df.columns = ['text']
        df.to_csv('wikt_token_en_split/en_' + str(count) +'.csv', index=False)
        count+=1

    file = open('wikt_token_en_split/log.txt','w')
    file.write(str(count))
    file.close()

# mw_splitting()