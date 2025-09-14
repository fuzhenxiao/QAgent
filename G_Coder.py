
from tools import *
from LLM import LLM_model
import os
import glob
import re


# The coder within Guided-few-shot Coding Agent
class G_Coder(object):
    def __init__(self, llm):
        self.system_prompt_generate='''You are a QASM expert, an assistant that writes  OpenQASM 3.0 code. produce valid QASM given: (a) examples, (b) algo_name, (c) qubit_number. Output qasm code only, nothing else.
        '''
        self.system_prompt_revise='''You are a QASM expert, an assistant that revises OpenQASM 3.0 code. modify QASM to fix issues given: (a) prior error_report, (b) potential_solution, (c) the previous QASM. Output qasm code only, nothing else.
        '''
        self.llm = llm

    def generate_code(self, examples,analysis,algo,qubit_num):

        prompt=f'''

        Here are some QASM examples for {algo} algorithm, which might be helpful.\n


        ### Analysis:\n
        {analysis}

        ### Related Example Code:\n
        {examples}\n

        Now, generate the code for the {algo} algorthm when qubit_number = {qubit_num} based on the examples, please only provide the code itself, nothing else.
        '''


        code=self.llm.generate(prompt, self.system_prompt_generate,max_tokens=10240)
        return clean_output(code)


    def regenerate_code(self,algo,qubit_num,code,error,suggestion):
        prompt=f'''
        the generated code for the {algo} algorithm when qubit_number = {qubit_num} was:\n
        {code}\n

        However, it encountered the following error: \n
        {error}\n

        The suggestion from another quantum expert is: \n
        {suggestion}\n

        Now, revise the code. Please only provide the code itself, nothing else.
        '''

        code=self.llm.generate(prompt, self.system_prompt_revise, max_tokens=10240)
        return clean_output(code)        



# === Test Code ===
if __name__ == "__main__":
    pass




    
    
