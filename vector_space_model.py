from Indexer import *
import pickle
import numpy as np
import os

def log_tf(ele):
    if ele:
        return 1+np.log(ele)
    else:
        return 0


temp = open('Cache/postingList.data','rb')
posting_list = pickle.load(temp)
temp.close()


temp = open('Cache/docSet.data','rb')
doc_set = pickle.load(temp)
temp.close()

print(len(posting_list.posting_list.values()))
print(len(doc_set.posting_list.keys()))

#
all_terms = list(posting_list.posting_list.keys())
term_to_idx = {}
for idx,term in enumerate(all_terms):
    term_to_idx[term]=idx

document_frequency = {}
for key,val in posting_list.posting_list.items():
    document_frequency[key] = val.get_Node_info()[0]

term_document_matrix = np.zeros((1990,35558))

for key,value in doc_set.posting_list.items():
    doc_terms = value.get_Node_info()[1]
    for k,v in doc_terms.items():
        term_document_matrix[key][term_to_idx[k]] = v

print('Document Matrix')
apply_log_df = np.vectorize(log_tf)
term_document_matrix = apply_log_df(term_document_matrix)
for key,val in document_frequency.items():
    idx_term = term_to_idx[key]
    term_document_matrix[:,idx_term] = term_document_matrix[:,idx_term]/val
print(term_document_matrix)

if not os.path.isdir('Cache1'):

    os.mkdir('Cache1')

    print('Saving Term Document Matrix')
    temp = open('Cache1/tdm.data','wb')
    pickle.dump(term_document_matrix,temp)
    temp.close()

    print('Saving Document Frequency')
    temp = open('Cache1/df.data','wb')
    pickle.dump(document_frequency,temp)
    temp.close()

    print('Saving All terms')
    temp = open('Cache1/at.data','wb')
    pickle.dump(all_terms,temp)
    temp.close()

    print('Saving Term to Index ')
    temp = open('Cache1/tdi.data','wb')
    pickle.dump(term_to_idx,temp)
    temp.close()


