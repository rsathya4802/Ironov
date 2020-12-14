import Indexer as Indexxer
from Indexer import main
import spell
data = Indexxer.DatasetLoader()
indexer = Indexxer.Indexer(data.speech_details)

indexer.posting_list.get_Node_info("iran")
spellChecker = spell.SpellChecker(Indexxer.word_Dict)
print("Enter the Query")
query = input()
print("Doing Spell checking on the query")
print("These are the corrections that we found")
spellChecker.correctSentence(query)