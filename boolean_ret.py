class BooleanRet:
    def __init__(self, indexer):
        self.indexer = indexer

    def AND_list(self, list1, list2):
        comm_list = []
        for elem in list1:
            if elem in list2:
                comm_list.append(elem)

        return comm_list

    def boolean_retrieval(self, words):

        if words == []:
            return []

        words_posting = []

        for word in words:
            posting_index = 0
            append_flag = True
            word_posting = list(
                self.indexer.posting_list.get_Node_info(word)[1].keys())
            l = len(word_posting)
            for i in range(len(words_posting)):
                posting_index = i
                if l < len(words_posting[i]):
                    append_flag = False
                    break
            if append_flag:
                words_posting.append(word_posting)
            else:
                words_posting.insert(posting_index, word_posting)

        result = words_posting[0]

        for i in range(1, len(words_posting)):
            result = self.AND_list(result, words_posting[i])

        return result
