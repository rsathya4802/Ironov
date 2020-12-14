import csv
import os
import spell
import pickle

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

# def intersect():


def boolean_retrieval(words, indexer):
    
    n = len(words)
    length = n
    if n == 0:

        return 
    word_set = set(words)
    
    posting = dict()
    for index, word in enumerate(word_set):
        insert = indexer.list_for_word(word)
        if insert:
            insert  = insert.keys()
            posting[index] = set(insert)
        else:
            index -= 1
    # print(posting)

    n = len(posting)

    if n % 2 != 0:
        last = posting[n - 1]
        del posting[n - 1]
        n -= 1
    
    new_post = dict()
    while (n > 1):
        n = len(posting)
        new_post.clear()
        j = 0
        for i in range(0, n,2):
            common = posting[i] & posting[i + 1]
            if (common):
                new_post[j] = common
            else:
                j -= 1
            
            j += 1
        
        posting = new_post
    
    if not bool(posting):
        return {}
    
    else:
        if length%2 != 0:
            common = posting[0] & last
            return common
        else:
            return posting[0]


    

        

    # lists = {}
    # for words in word_set:



data = DatasetLoader()
indexer = Indexer(data.speech_details)
indexer.posting_list.get_Node_info("iran")
spellChecker = spell.SpellChecker(word_Dict)
iran = indexer.list_for_word("delhi")
# print(iran)
print(iran.keys())
print("Enter the Query")
query = input()
print("Doing Spell checking on the query")
print("Following is the query after spell correction")

# qyery formulation ofr boolean retrieval
query_word = query.split()
spell_correct_query = []
# print(spellChecker.correctSentencePerWord("deli"))

for word in query_word:
    result = spellChecker.correctSentencePerWord(word)
    # print(result)
    if result in word_Dict:
        spell_correct_query.append(result)


print(spell_correct_query)

print(boolean_retrieval(spell_correct_query,indexer))


