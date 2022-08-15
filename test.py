import mongodb_con as db_con
import wordnet_extraction as we
import wikt_token_en_split_extracting as wikt_extract

# print(db_con.check_token("winnie"))

# db_con.export_to_list_n_df(db_con.mongo_token(), "tokens.csv")

# x = db_con.read_all(db_con.mongo_token())
# print(x)

# db_con.remove_all_tokenrecords(db_con.mongo_token())

# db_con.export_to_list_n_df(db_con.mongo_oov(), "mongo_oov.csv")
# db_con.remove_all_oovrecords()

wikt_extract.mw_system()


# import wikt_token_json_extracting as wt
# wt.extracting_norm_mw_directory()

# x = we.wn_system(2)

