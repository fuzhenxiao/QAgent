from tools import RAG,SearchEngine
from LLM import LLM_model
#from Internet_Agent import *
from Prompt_Agent import *
import os
import glob
import re


class Reflection_Agent(object):

    def __init__(self, llm,internet):
        self.llm = llm
        self.internet=internet

    def generate_reflection(self,init_template,codes=[],reports=[]):

        for i in range(0,len(codes)):
            init_template+=f'''
            tried to this code:\n
            {codes[i]}\n
            but received the following error:\n
            {reports[i]}\n
            '''

        template=init_template+'Now, analyze the error and provide possible solution. Please provide the analysis and solution only, nothing else is needed.'

        reflection=self.llm.generate(template, role="reflection", max_tokens=1024)

        return reflection


# === Test Code ===
if __name__ == "__main__":
    pass





    
    
