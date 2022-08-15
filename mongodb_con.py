import pandas as pd
import pymongo

def mongo_init():
    client = pymongo.MongoClient("mongodb+srv://pc6:pc60303@cluster0.dh3cz.mongodb.net/?retryWrites=true&w=majority")
    return client

client = mongo_init()

def mongo_melex(client=client,database="melex"):
    mydb = client[database]
    return mydb

mydb = mongo_melex()

def mongo_token(database="token"):
    mytoken = mydb[database]
    return mytoken

def mongo_oov(database="oov"):
    myoov = mydb[database]
    return myoov

def mongo_kamusdewan(database="malay_sourceKD"):
    kamusdewan = mydb[database]
    return kamusdewan

def mongo_listdb(client=client):
    return client.list_database_names()

def mongo_listcl(db = mongo_melex()):
    return db.list_collection_names()

def mongo_api_found_term(database="api_found_term"):
    api_found_term = mydb[database]
    return api_found_term

def mongo_api_not_found_term(database="api_not_found_term"):
    api_not_found_term = mydb[database]
    return api_not_found_term

def mongo_oov_dup_term(database="oov_dup_term"):
    oov_dup_term = mydb[database]
    return oov_dup_term

def mongo_melex_dup_term(database="melex_dup_term"):
    melex_dup_term = mydb[database]
    return melex_dup_term

def check_token(token, collection=mongo_token()):
    return collection.count_documents({"token":token})

def check_oov(oov, collection=mongo_oov()):
    return collection.count_documents({"token":oov})

def check_api_found_term(token, collection=mongo_api_found_term()):
    return collection.count_documents({"token":token})

def check_api_not_found_term(token, collection=mongo_api_not_found_term()):
    return collection.count_documents({"token":token})

def check_oov_dup_term(token, collection=mongo_oov_dup_term()):
    return collection.count_documents({"token":token})

def check_melex_dup_term(token, collection=mongo_melex_dup_term()):
    return collection.count_documents({"token":token})

def insert_single_oov(data, remark="", language="en",collection=mongo_oov()):
    try:
        collection.insert_one({"token":data, "language_detected":language,"remark":remark})
    except Exception as e:
        print("An exception occurred")
        print(e)

def insert_api_found_term(data, remark="", language="en",collection=mongo_api_found_term()):
    try:
        collection.insert_one({"token":data, "language_detected":language,"remark":remark})
    except Exception as e:
        print("An exception occurred")
        print(e)

def insert_api_not_found_term(data, remark="", language="en",collection=mongo_api_not_found_term()):
    try:
        collection.insert_one({"token":data, "language_detected":language,"remark":remark})
    except Exception as e:
        print("An exception occurred")
        print(e)

def insert_oov_dup_term(data, remark="", language="en",collection=mongo_oov_dup_term()):
    try:
        collection.insert_one({"token":data, "language_detected":language,"remark":remark})
    except Exception as e:
        print("An exception occurred")
        print(e)

def insert_melex_dup_term(data, remark="", language="en",collection=mongo_melex_dup_term()):
    try:
        collection.insert_one({"token":data, "language_detected":language,"remark":remark})
    except Exception as e:
        print("An exception occurred")
        print(e)

def remove_all_oovrecords(collection=mongo_oov()):
    print("This step cannot be undone!")
    val = input("Re-enter the collection name to be remove: ")
    
    if val=="oov":
        print("This step cannot be undone!")
        val = input("Re-enter the collection name to be remove: ")
        
        if val=="oov":
            collection.delete_many({})

def remove_all_tokenrecords(collection=mongo_token()):
    print("This step cannot be undone!")
    val = input("Re-enter the collection name to be remove: ")
    
    if val=="token":
#         here should add in backup file
# soon
        print("This step cannot be undone!")
        val = input("Re-enter the collection name to be remove: ")
        
        if val=="token":
            collection.delete_many({})

def read_all(collection):
    data = collection.find()
    return data
    # for x in mycol.find():
    #     print(x)

def read_token(collection, key_word):
    for x in collection.find({"token":key_word}):
        print(x)

def read_postag(collection, key_tag):
    for x in collection.find({"pos_tag":key_tag}):
        print(x)

def read_token_postag(collection, key_tag,key_word):
    for x in collection.find({"pos_tag":key_tag},{"token":key_word}):
        print(x)

def export_to_list_n_df(mongo_db,filename="default.csv"):
    x = read_all(mongo_db)
    list_x = list(x)
    df_x = pd.DataFrame(list_x)
    df_x.to_csv(filename)
    return list_x,df_x

# please consider
# insert token first or context value first 
def insert_mwdata_multiple_contexts(token_str, context_list_of_dict, collection=mongo_token(), remarks = "testing"):
    try:
        collection.insert_one({"token":token_str, "contexts": context_list_of_dict, "context_count": len(context_list_of_dict),"remarks": remarks})
    except Exception as e:
        print("An exception occurred")
        print(e)


def find_countext_count(token): 
    context_count = 0
    word_context = mongo_token().find({'token':token}, {"context_count"})
    for i in word_context:
        context_count = int(i["context_count"])
    return context_count


# this function aims to update single context only 
def update_context_WN(collection, token, context):
    # get context count (straight start with context count value)
    context_count = find_countext_count(token)
    print(context_count)
    print(context_count+1)
    # collection.update_one({'token':token}, {"$set": {"Location": "New York"}})
    # {"$push": {"key.some_other_key":"value"}}
    collection.update_one({'token':token}, {"$push": {"contexts":context}})
    # update context_count value in the database 
    collection.update_one({'token':token}, {"$set": {"context_count": context_count+1}})


# fullfilling condition 4 
# inserting a new word that did not exsit in database before hand 
# if it is found in OOV, any column need to update? 
def insert_wndata(token_str, context_list_of_dict, collection=mongo_token(), remarks = "WN first run -1"):
    try:
        collection.insert_one({"token":token_str, "contexts": context_list_of_dict, "context_count": len(context_list_of_dict),"remarks": remarks})
    except Exception as e:
        print("An exception occurred")
        print(e)

# this function aims to update single context only for Merriam Webster
def update_context_MW(collection, token, context):
    # get context count (straight start with context count value)
    context_count = find_countext_count(token)
    print(context_count)
    print(context_count+1)
    collection.update_one({'token':token}, {"$push": {"contexts":context}})
    collection.update_one({'token':token}, {"$set": {"context_count": context_count+1}})