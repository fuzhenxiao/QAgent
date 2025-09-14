import ast
import io
import sys
import importlib.util
import traceback
from tools import *
from LLM import LLM_model
import signal
import ast

# The coder within Tools-Augmented Coding Agent
class T_Coder:
    def __init__(self, llm):

        self.llm = llm

        self.system_prompt_generate='''You are a quantum expert, an assistant that writes python code using provided tools (tools designed to generate qasm code). produce valid python given: (a) tools description, (b) plan, (c) algorithm name, (d) qubit_number. Output python code only, nothing else.
        '''
        self.system_prompt_revise='''You are a quantum expert, an assistant that revises python code using provided tools. modify python code to fix issues given: (a) algorithm name (b) qubit number (c) prior code (d) prior error_report, (e) potential_solution. Output python code only, nothing else.
        '''

    def generate_code(self, tools_description, plan, algo,qubit_num):

        prompt=f'''

        Here are the tools (functions) that are already implemented. You can use them for {algo} algorithm, which might be helpful.\n

        ### Tools (Functions) Available:\n
        {tools_description}

        ### Suggested Plan:\n
        {plan}\n

        Now, generate the code for the {algo} algorthm when qubit_number = {qubit_num} using these existing tools. You can choose to rewrite you own version of them, But I recommend to call these functions directly.
        Output python code directly without any comment or explanation. I will load these functions by myself and execute your codes directly.
        If you are calling existing tools, avoid importing modules since these tools can run without additional lib. 
        '''

        code=self.llm.generate(prompt, self.system_prompt_generate,max_tokens=10240)
        if code.startswith('```python'):
            code = code.strip('```python').strip('```').strip()
        return code


    def regenerate_code(self,algo,qubit_num,code,error,suggestion):
        prompt=f'''
        the generated python code (based on pre-defined tools) for the {algo} algorithm when qubit_number = {qubit_num} was:\n
        {code}\n

        However, it encountered the following error: \n
        {error}\n

        The suggestion from another expert is: \n
        {suggestion}\n

        Now, revise the code. Please only provide the python code itself, nothing else.
        '''

        code=self.llm.generate(prompt, self.system_prompt_revise, max_tokens=10240)
        if code.startswith('```python'):
            code = code.strip('```python').strip('```').strip()
        return code     




if __name__ == "__main__":
    pass