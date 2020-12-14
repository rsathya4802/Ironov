import pickle
import numpy as np

def log_tf(ele):
    if ele:
        return float(1+np.log(ele))
    else:
        return 0.0

def cosine_similarity(vec1,vec2):
    return np.dot(vec1,vec2)/(np.linalg.norm(vec1)*np.linalg.norm(vec2))


def get_cosine_scores(query):
    cosine_scores = [(cosine_similarity(term_document_matrix[i,:],query),i) for i in range(term_document_matrix.shape[0])]
    cosine_scores.sort(key=lambda x:x[0],reverse=True)
    return cosine_scores


temp = open('Cache1/at.data','rb')
all_terms = pickle.load(temp)
temp.close()

temp = open('Cache1/tdi.data','rb')
term_to_idx = pickle.load(temp)
temp.close()

temp = open('Cache1/df.data','rb')
document_frequency = pickle.load(temp)
temp.close()

temp = open('Cache1/tdm.data','rb')
term_document_matrix = pickle.load(temp)
temp.close()

print('Enter Query: ')
query = input()
# query = 'donald trump usa'
query_terms = query.strip().split()
q_vector = np.zeros((1,35558))

for word in query_terms:
    if word in all_terms:
        q_vector[0][term_to_idx[word]]+=1

apply_log_df = np.vectorize(log_tf)
q_vector = apply_log_df(q_vector)
for word in all_terms:
        q_vector[0][term_to_idx[word]] = q_vector[0][term_to_idx[word]]/document_frequency[word]

n = 15
cosine_scores = get_cosine_scores(q_vector[0,:])
print('Search Results: ')
for ele in cosine_scores[:n]:
    print(ele[1],ele[0])
