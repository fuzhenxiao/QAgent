
from tools import *
import os
import glob
import re
import ast
import random

# The advisor within Guided-few-shot Coding Agent
class G_Advisor(object):

    def __init__(self, llm):
        self.llm = llm
        self.system_prompt='You are an expert in quantum programming, especially good at using qasm language.'
        

    def conclude_coding_info(self, algo='',shots=3):


        example_qubit_num_pool=[]
        for i in range(2,2+shots):
            example_qubit_num_pool.append(i)
        matches = []
        for n in example_qubit_num_pool:
            pattern_path = f'./kernels/{algo}/qasm_circuit/*_n{n}.qasm'
            matches.extend(glob.glob(pattern_path))

        pattern = re.compile(r'.*_n(\d+)\.qasm$')
        result_lines = []
        for idx, file_path in enumerate(matches, start=1):
            match = pattern.search(file_path)
            #print('found file ',file_path)
            if match:
                n_value = match.group(1)
                with open(file_path, 'r') as f:
                    content = f.read().strip()
                result_lines.append(f'\n### Example {idx}, when qubit_number = {n_value}: the qasm code is \n {content} \n')
        print(f'selected {len(matches)} examples for {algo}')

        examples = '\n'.join(result_lines)

        template = f'''

        ### Related Example Code:\n
        These QASM example codes might be helpful while generating qasm code for {algo} algorithm:\n
        {examples}\n
        '''

        prompt_postfix = 'Your task is to create a chain of thought explaining these example codes, so that it can be used to further guide coders to create best QASM to solve the problem. Please only provide the chain of thought process, nothing else'
        prompt = template + prompt_postfix

        analysis = self.llm.generate(prompt,self.system_prompt, max_tokens=1024)
        return examples, analysis,algo





# === Test Code ===
if __name__ == "__main__":
    pass
    
    
