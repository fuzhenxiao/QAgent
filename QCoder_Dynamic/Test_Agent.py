
from tools import RAG,SearchEngine
from LLM import LLM_model
#from Internet_Agent import *
from Prompt_Agent import *
import os
import glob
import re


import re

def extract_number(string):
    result = re.search(r'\d+', string)
    if result:
        return int(result.group(0))
    else:
        return None 

class Test_Agent(object):

    def __init__(self, llm,rag):
        self.llm = llm
        self.RAG=rag

    def get_n(self, question):
        n=self.llm.generate(question, role="n", max_tokens=20)
        return n

    def get_algo_name(self,question):
        related_path = self.RAG.search(question+',description', top_k=1)[0][0]
        parts = related_path.split(os.sep)
        algo_name=parts[4]

    def get_oracles_and_test_code(self, question):
        n=self.get_n(question)
        algo_name=self.get_algo_name(question)

    def get_n_and_test_script(self,question):
        related_path = self.RAG.search(question+',description', top_k=1)[0][0]
        parts = related_path.split(os.sep)
        algo_name=parts[4]
        script_path = os.sep.join(parts[:5]) + os.sep+'universal_test.py'

        n=self.get_n(question)
        n=extract_number(n)
        if n==None:
            return 0,script_path
        else:
            return int(n),script_path



# === Test Code ===
if __name__ == "__main__":
    pass



    
    
