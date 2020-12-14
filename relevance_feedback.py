from ranking import *

print('RELEVANCE FEEDBACK')
print('Which documents do you think are relevant: ')
relevant_docs =  list(map(int,input().split()))
relevant_docs = [x-1 for x in relevant_docs]
non_relevant_docs = []
for i in range(n):
    if i not in relevant_docs:
        non_relevant_docs.append(i)
relevant_doc_ids = [cosine_scores[i][1] for i in relevant_docs]
non_relevant_doc_ids = [cosine_scores[i][1] for i in non_relevant_docs]

print('Relevant Documents',relevant_doc_ids)
print('Non Relevant Documents',non_relevant_doc_ids)
beg = term_document_matrix[0,:]

alpha = 1
beta = 0.75
gamma = 0.15

relevant_sum = term_document_matrix[relevant_doc_ids[0],:]
for i in range(1,len(relevant_doc_ids)):
    relevant_sum+= term_document_matrix[relevant_doc_ids[i],:]
non_relevant_sum = term_document_matrix[non_relevant_doc_ids[0],:]
for i in range(1,len(non_relevant_doc_ids)):
    non_relevant_sum+= term_document_matrix[non_relevant_doc_ids[i],:]
print('Query before relevance feedback')
print(q_vector[0,:])

q_vector[0,:] = alpha*q_vector[0,:] + beta*(1/len(relevant_docs))*relevant_sum - gamma*(1/len(non_relevant_docs))*non_relevant_sum

print('Query after relevance feedback')
print(q_vector[0,:])

cosine_scores = get_cosine_scores(q_vector[0,:])

print('Search Results after relevance feedback: ')
for ele in cosine_scores[:n]:
    print(ele[1],ele[0])