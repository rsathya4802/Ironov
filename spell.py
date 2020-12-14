import json
import math


class Trie:

    def __init__(self, val=None, parent=None):
        self.child = {}
        self.parent = parent
        self.val = val

    def insert(self, word):
        parent = self
        curr = self.child
        for ch in word:
            if ch not in curr:
                curr[ch] = Trie(ch, parent)
            parent = curr[ch]
            curr = curr[ch].child
        curr['#'] = Trie('#', parent)

    def findWord(self, word):
        curr = self
        for ch in word:
            if ch not in curr.child:
                return False
            curr = curr.child[ch]
        return '#' in curr.child

    def findSpecialWord(self, word_k):
        i = 0
        word, k = word_k
        if word == '':
            return []
        l = len(word)
        node_bucket = [self]
        last_node = self
        while i < l:
            w = word[i]
            c = 0
            if w == '?':
                c = 1
            elif w == '^':
                c = 2
            while node_bucket != []:
                node = node_bucket[0]
                if c == 0 and w in node.child:
                    node_bucket.append(node.child[w])
                elif c == 1:
                    node_bucket.extend([node.child[n]
                                        for n in node.child if n != '#'])
                elif c == 2:
                    node_bucket.extend(
                        [node.child[n] for n in node.child if n not in (word[i+1], '#')])
                p = node_bucket.pop(0)
                if p == last_node:
                    if node_bucket == []:
                        return node_bucket
                    last_node = node_bucket[-1]
                    if c == 2:
                        i += 1
                    break
            i += 1

        final_words = []

        for node in node_bucket:
            if '#' in node.child:
                final_words.append(Trie.PrintFromNode(node))
        return [(x, k) for x in set(final_words)]

    @staticmethod
    def PrintFromNode(node):
        str = ""
        curr = node
        while curr.parent != None:
            str = curr.val + str
            curr = curr.parent
        return str

    def __repr__(self):
        return self.val


class SpellChecker:

    def getrelevance(self, word_k):
        score = 0
        word, k = word_k
        score_k = {'1': 100, '2': 10, 'other': 0.2}
        score += score_k[str(k) if str(k) in ('1', '2')
                        else 'other']*math.log(self.word_Dict[word]+1, 10)

        return score

    @staticmethod
    def loadJson(file_name):
        f = open(file_name, 'r')
        data = json.load(f)

        return data

    def loadTrie(self):
        for word in self.word_Dict:
            self.word_Trie.insert(word)

    def __init__(self, word_Dict):
        print("Loading default Data")
        self.word_Dict = word_Dict
        print(len(self.word_Dict), "words found")
        print("Building Trie")
        self.word_Trie = Trie()
        self.loadTrie()
        print("Done!")
        # print(self.word_Trie.findSpecialWord("e?mllo"))
        # print(self.genByEditDist("ab",2))?
        # print(self.Substitution_gen("abcd",4))

    def findCorrect(self, word):
        word = word.lower()
        words = set()
        if word.isalpha():
            if self.word_Trie.findWord(word):
                words.add((word, 1000))
                return words
            else:
                edit_word = self.genByEditDist(word, 2)
                for pattern in edit_word:
                    words.update(self.word_Trie.findSpecialWord(pattern))

        return [(x[0], self.getrelevance(x)) for x in words]

    @staticmethod
    def checkExists(word, best):
        i = 0
        while i < len(best):
            if best[i][0] == word:
                return i
            i += 1

        return -1

    def getNBest(self, related_words, n):
        best = []
        c = 0
        for word_k in related_words:
            word, score = word_k
            exist = SpellChecker.checkExists(word, best)
            if exist != -1:
                if best[exist][1] < score:
                    best.pop(exist)
                    c -= 1
            i = 0
            while i < c and score <= best[i][1]:
                i += 1
            if i < n:
                best.insert(i, word_k)
                c += 1
            if c >= n:
                best.pop()
                c -= 1

        return best

    @staticmethod
    def cleanString(sent):
        i = 0
        l = len(sent)
        cln_str = ""
        while i < l:
            w = sent[i]
            if w != '^':
                cln_str += w
            else:
                while i < l and sent[i] == '^':
                    i += 1

                if i >= l:
                    break
                else:
                    cln_str += '^'+sent[i]

            i += 1
        return cln_str.replace('^?', '?')

    @staticmethod
    def Deletion_gen(word, l):
        return [SpellChecker.cleanString(word[:i] + word[i+1:]) for i in range(l)]

    @staticmethod
    def Insertion_gen(word, l):
        return [SpellChecker.cleanString(word[:i] + '?' + word[i:]) for i in range(l+1)]

    @staticmethod
    def Swapper_gen(word, l):
        return [SpellChecker.cleanString(word[:i] + word[i+1]+word[i] + word[i+2:]) for i in range(l-1)]

    @staticmethod
    def Substitution_gen(word, l):
        return [SpellChecker.cleanString(word[:i] + '^' + word[i:]) for i in range(l)]

    @staticmethod
    def genByEditDist(word, k):
        pattern_bucket = [(word, 0)]
        for i in range(k):
            temp_bucket = []
            for pattern, _ in pattern_bucket:
                l = len(pattern)
                temp_bucket.extend(SpellChecker.Deletion_gen(pattern, l))
                temp_bucket.extend(SpellChecker.Insertion_gen(pattern, l))
                temp_bucket.extend(SpellChecker.Swapper_gen(pattern, l))
                temp_bucket.extend(SpellChecker.Substitution_gen(pattern, l))
            pattern_bucket.extend([(x, i+1) for x in temp_bucket])
            if i == 0:
                pattern_bucket.pop(0)

        return set(pattern_bucket)

    def getBestCandidate(self, word, n):
        return self.getNBest(self.findCorrect(word), n)

    def correctSentence(self, sent, n=2, fil=None):
        sent = sent.lower().split()
        for word in sent:
            best_candidate = self.getBestCandidate(word, n)
            if best_candidate == []:
                if fil == None:
                    print(word+' -> <unknown>')
                else:
                    print(word+'<unknown>', end=" ", file=fil)
            elif best_candidate != [] and best_candidate[0][0] != word:
                if fil == None:
                    print(word+' -> '+','.join([x[0] for x in best_candidate]))
                else:
                    print(
                        word+'{'+'|'.join([x[0] for x in best_candidate]), end='} ', file=fil)
            else:
                if fil != None:
                    print(word, end=" ", file=fil)
        if fil != None:
            print('', file=fil)
    
    # get the best spell correct word for a given query
    # by abhinav
    def correctSentencePerWord(self, sent, n=2, fil=None):
        best_candidate = self.getBestCandidate(sent, 2)
        return best_candidate[0][0]