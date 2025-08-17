
from tools import RAG,SearchEngine
from LLM import LLM_model
#from Internet_Agent import *
from Prompt_Agent import *
import os
import glob
import re
class Coding_Agent(object):

    def __init__(self, llm):
        self.llm = llm

    def generate_code(self, question, examples, analysis):

        template=f'''
        The quantum algorithm problem is described below:\n
        ### Problem:\n
        {question}\n

        ### Analysis:\n
        {analysis}

        ### Related Example Code:\n
        These QASM example codes might be helpful:\n
        {examples}\n

        Now, generate the code for the question. Please only provide the code itself, nothing else
        '''

        code=self.llm.generate(template, role="circuit", max_tokens=10240)
        return code,template

    def generate_n_code(self, prompt,n=3,temp=0.8,top_p=0.95):


        code=self.llm.generate(template, role="circuit", max_tokens=10240)
        return code

    def regenerate_code(self,init_template,codes=[],reports=[]):

        for i in range(0,len(codes)):
            init_template+=f'''
            tried to this code:\n
            {codes[i]}\n
            but received the following error:\n
            {reports[i]}\n

            '''

        template=init_template+'Now, generate the code for the question, please only provide the code itself, nothing else'

        code=self.llm.generate(template, role="circuit", max_tokens=10240)
        return code
        



# === Test Code ===
if __name__ == "__main__":
    pass




    
    
