from LLM import LLM_model
import os
import glob
import re
import ast
import yaml
import importlib
from tools import *



# The advisor within Tools-Augmented Coding Agent
class T_Advisor(object):

    def __init__(self, llm):
        self.llm = llm
        self.system_prompt='You are an expert in quantum area. You will be provided with some tools to generate quantum circuit. Your task is to generate a plan to use these tools'
        

    def conclude_coding_info(self, algo=''):
        tools_description = load_algorithm_tools(algo)
        prompt=f'''
        You are an intelligent Python agent equipped with a set of pre-defined Python functions (all related to certain quantum algorithms).
        Your job is to make a plan to generate quantum qasm circuit for {algo}.
        You can make the decision to generate new functions, but I recommend using existing functions.
        Sometimes (Not Always) it is necessary to use fake oracles. But do remember to exclude it later. 
        The Real oracle function has already been provided as a black-box oracle gate named "Oracle" in the "oracle.inc"
        In your plan, mention to print out the corresponding qasm circuit so that I can easily capture it via stdout. 

        Available functions (they are already implemented and ready to be called directly):
        {tools_description}

        Output the high-level plan using natural language only, nothing else. At this step, detailed python code is not needed
        for example:
        step 1 is to initialize the template circuit.
        step 2 is to generate necessary parameters.
        step 3 is to generate the input and output quantum registers.
        step 4 is to generate the complete cirucit.
        step 5 is to turn QuantumCircuit into a QASM string.
        step 6 is to print it out.
        '''
        plan = self.llm.generate(prompt, self.system_prompt,1024)

        return tools_description, plan,algo



# === Test Code ===
if __name__ == "__main__":
    pass
    

    
    
