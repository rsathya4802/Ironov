import csv
import os
import spell
import pickle
import SDT_calc
import math
# import boolean_ret

word_Dict = {}


class WordsList:
    def buildWordList(self, filename):
        file = open(filename, 'r')

        for line in file:
            self.words.append(line.strip())

    def __init__(self, filename):
        self.words = []
        self.buildWordList(filename)

    def isInList(self, word):
        return word in self.words


class Posting_List_Node:
    def __init__(self):
        self.list_entries_count = 0
        self.entries = {}

    def add_to_list(self, entry_key):
        if entry_key not in self.entries:
            self.entries[entry_key] = 0
            self.list_entries_count += 1
            if entry_key in word_Dict:
                word_Dict[entry_key] += 1
        self.entries[entry_key] += 1

    def get_Node_info(self):
        return (self.list_entries_count, self.entries)
    # new method by abhinav

    def get_Node_info2(self):
        return (self.entries)


class Posting_List:
    def __init__(self):
        self.posting_list = {}

    def add_to_posting(self, key, entry_key):
        if key not in self.posting_list:
            self.posting_list[key] = Posting_List_Node()
        self.posting_list[key].add_to_list(entry_key)

    def get_Node_info(self, key):
        return self.posting_list[key].get_Node_info()

    # new method by abhinav to return posting for a key
    # without the key
    def get_Node_info2(self, key):
        if key in self.posting_list:
            return self.posting_list[key].get_Node_info2()
        else:
            return None


class DatasetLoader:

    def removeNonASCII(self, text):
        return ''.join([i if i.isalnum() else ' ' for i in text])

    def ReadDataset(self, DATASET_LOC='Dataset/'):
        for fname in os.listdir(DATASET_LOC):
            with open(DATASET_LOC+fname, 'r', encoding='utf-8') as csv_file:
                csv_reader = csv.reader(csv_file)
                keys = []
                keys_loaded = False
                for row in csv_reader:
                    if not keys_loaded:
                        keys_loaded = True
                        keys = row
                    else:
                        self.speech_details.append({keys[i]: self.removeNonASCII(row[i]) if keys[i] == keys[-2] or keys[i] == keys[-1] else row[i]
                                                    for i in range(len(keys))})

    def __init__(self):
        print("Loading the dataset")
        self.speech_details = []
        self.ReadDataset()
        print("Dataset Loaded")


class Indexer:

    def ProcessDataset(self, dataset):
        doc_id = 0
        for data in dataset:
            if doc_id % 100 == 0:
                print(doc_id, "documents done")
            content_keys = ('info', 'speech')
            for key in content_keys:
                for word in data[key].split(' '):
                    lower_word = word.lower()
                    if lower_word not in word_Dict and lower_word.isalpha():
                        word_Dict[lower_word] = 1
                    if lower_word == '' or self.stopWords.isInList(lower_word):
                        continue
                    else:
                        self.posting_list.add_to_posting(lower_word, doc_id)
                        self.doc_set.add_to_posting(doc_id, lower_word)
            doc_id += 1

    def list_for_word(self, word):
        return self.posting_list.get_Node_info2(word)

    def __init__(self, dataset):

        global word_Dict

        CACHE_DIR = "Cache"

        if os.path.isdir(CACHE_DIR):

            print("Loading Cached data")

            f_stopWords = open(CACHE_DIR+"/stopWords.data", 'rb')
            f_postingList = open(CACHE_DIR+"/postingList.data", 'rb')
            f_docSet = open(CACHE_DIR+"/docSet.data", 'rb')
            f_wordDict = open(CACHE_DIR+"/wordDict.data", 'rb')

            self.stopWords = pickle.load(f_stopWords)
            self.posting_list = pickle.load(f_postingList)
            self.doc_set = pickle.load(f_docSet)
            word_Dict = pickle.load(f_wordDict)

            print("Loaded Cached Data")

        else:
            print("Indexing")

            os.mkdir(CACHE_DIR)

            f_stopWords = open(CACHE_DIR+"/stopWords.data", 'wb')
            f_postingList = open(CACHE_DIR+"/postingList.data", 'wb')
            f_docSet = open(CACHE_DIR+"/docSet.data", 'wb')
            f_wordDict = open(CACHE_DIR+"/wordDict.data", 'wb')

            self.stopWords = WordsList("stop_words.txt")
            self.posting_list = Posting_List()
            self.doc_set = Posting_List()

            self.ProcessDataset(dataset)

            pickle.dump(self.stopWords, f_stopWords)
            pickle.dump(self.posting_list, f_postingList)
            pickle.dump(self.doc_set, f_docSet)
            pickle.dump(word_Dict, f_wordDict)

            print("Data Indexed")
        # print(self.posting_list.get_Node_info("hello"))
        # print(self.doc_set.get_Node_info(0))
        # print(len(word_Dict), word_Dict['iran'])

# calculate score
def cal_score(binary_index, p, u, word_list):
    score = 0
    for index, word in enumerate(binary_index):
        if word == 1:
            if 1 - p[index] != 0:
                if p[index] != 0:
                    score += round(math.log(round(p[index] / (1 - p[index]), 2), 2), 4)
                else:
                    score += -100000000
            else:
                score += 100000000
            
            if u[index] != 0:
                if 1 - u[index] != 0:
                    score += round(math.log(round((1 - u[index]) / u[index], 2), 2), 4)
                else:
                    score += -100000000
            else:
                score += 100000000
    
    if score == 0:
        score = -100000000

    return score

# recursive method
def probabilstic_model(ranking, S, word_list, N, u, p,term_count,binary_index,s):
    
    for  indx, doc in enumerate(s):
        s[indx] = 0

    for index, doc in enumerate(ranking):
        if index > S:
            break
        else:
            for idx, word in enumerate(binary_index[doc]):
                if word == 1:
                    s[idx] += 1

    for i, word in enumerate(word_list):
        p[i] = round(term_count[i] / S, 4)

    for i,word in enumerate(word_list):
        u[i] = round((term_count[i] - s[i]) / (N - S), 4)
    
    new_ranking = ranking
    for doc in binary_index:
        score = cal_score(binary_index[doc], p, u, word_list)
        new_ranking[doc] = score
    
    new_ranking = dict(sorted(ranking.items(), key=lambda item: item[1], reverse=True))
    print(new_ranking)
    if cmp(new_ranking, ranking) == 0:
        return ranking
    
    else:
        return probabilstic_model(new_ranking,S,word_list,N,u,p,term_count,binary_index,s)

# first loop of probability model
def probabilistic_result(word_list, retrieved_doc,indexer):
    
    ranking = {}
    for docs in retrieved_doc:
        ranking[docs] = 1.0
    ranking_result = dict(sorted(ranking.items(), key=lambda item: item[1], reverse=True))

    binary_index = {}
    for doc in retrieved_doc:
        binary_index[doc] = ([int(word in indexer.doc_set.get_Node_info(doc)[1]) for word in word_list])

    p = []
    for word in word_list:
        p.append(0.5)
    N = 0
    for doc in binary_index:
        for word in binary_index[doc]:
            if word == 1:
                N += 1
    term_count = []
    for word in word_list:
        term_count.append(0)
    
    for doc in binary_index:
        for index, word in enumerate(binary_index[doc]):
            if word == 1:
                term_count[index] += 1
    print(term_count)
    u = []
    for ind, word in enumerate(word_list):
        u.append(round(term_count[ind] / N, 2))
    # print(ranking)
    for doc in binary_index:
        score = cal_score(binary_index[doc], p, u, word_list)
        ranking[doc] = score
    ranking = dict(sorted(ranking.items(), key=lambda item: item[1], reverse=True))
    s = []
    for word in word_list:
        s.append(0)
    ranking = probabilstic_model(ranking, 20, word_list, N, u, p, term_count, binary_index, s)
    print(ranking)
    return ranking







# given a normal query convert it to boolean OR query
def probabilistic_boolean_query(wordset):
    final_query = ""
    for word in wordset:
        if word != wordset[-1]:
            final_query += word + " | "
        else:
            final_query += word + " !"
    
    
    return final_query





data = DatasetLoader()
indexer = Indexer(data.speech_details)
spellChecker = spell.SpellChecker(word_Dict)

sdt = SDT_calc.SDT(indexer, data.speech_details)

print("Enter the Query")
query = input()
print("Doing Spell checking on the query")
print("Following is the query after spell correction")

# qyery formulation ofr boolean retrieval
query_word = [x.lower() for x in query.split()]
spell_correct_query = []

error_flag = False

for word in query_word:
    if word in sdt.non_terminals:
        spell_correct_query.append(word)
    else:
        result = spellChecker.correctSentencePerWord(word)
        if result == "<unknown>":
            error_flag = True
            spell_correct_query.append(result)
            print(result)
        if result in word_Dict:
            spell_correct_query.append(result)


# print(' '.join(spell_correct_query))
# print(spell_correct_query+['!'])

boolean_spell_correct_query = probabilistic_boolean_query(spell_correct_query)
print(spell_correct_query)
print(boolean_spell_correct_query)
boolean_spell_correct_query = boolean_spell_correct_query.split()


if error_flag:
    print("Unknown words found. Terminating!")
else:
    retrieved_list = sdt.calc(boolean_spell_correct_query)
    print(retrieved_list)

# ranked list of docs is recieved , get top 20
top_20_relevant_docs = probabilistic_result(spell_correct_query,retrieved_list,indexer)
