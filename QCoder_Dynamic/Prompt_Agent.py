
from tools import RAG,SearchEngine
from LLM import LLM_model
#from Internet_Agent import *
import os
import glob
import re
import ast
import random

def extract_oracle_function(algo_name):
    file_path = f'./QCircuitNet_Dataset-simplified/Algorithm_Design/Quantum_Computing/{algo_name}/{algo_name}_dataset.py'
    target_func = f'{algo_name}_oracle'

    with open(file_path, 'r') as f:
        source = f.read()

    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == target_func:
            start_line = node.lineno
            end_line = node.end_lineno if hasattr(node, 'end_lineno') else None
            if end_line is None:
                raise RuntimeError("Python version too old: `end_lineno` not available.")
            lines = source.splitlines()
            func_source = "\n".join(lines[start_line - 1:end_line])
            return func_source
    raise ValueError(f"Function `{target_func}` not found in `{file_path}`.")

class Prompt_Agent(object):

    def __init__(self, llm,rag,internet_agent=None):
        self.llm = llm
        self.RAG = rag
        self.internet_agent=internet_agent



    def generate_coding_info(self, question='', question_n=3, shots=5):
        related_path = self.RAG.search(question + ',description', top_k=1)[0][0]
        parts = related_path.split(os.sep)
        algo_name = parts[4]
        related_path = os.sep.join(parts[:5]) + os.sep
        matches = []
        for n in range(3, 11):
            if n == question_n:
                continue
            matches.extend(glob.glob(f'{related_path}qasm_circuit/*_n{n}.qasm'))


        selected_matches = random.sample(matches, min(shots, len(matches)))
        print(f'selected {len(selected_matches)} examples')


        pattern = re.compile(r'.*_n(\d+)\.qasm$')
        result_lines = []
        for idx, file_path in enumerate(selected_matches, start=1):
            match = pattern.search(file_path)
            if match:
                n_value = match.group(1)
                with open(file_path, 'r') as f:
                    content = f.read().strip()
                #print(f'for n={question_n}, {file_path} was selected as example')
                result_lines.append(f'\n### Example {idx}, when n={n_value}: {content} \\n')

        examples = '\n'.join(result_lines)

        template = f'''
        The quantum algorithm problem is described below:\n
        ### Problem:\n
        {question}\n

        ### Related Example Code:\n
        These QASM example codes might be helpful:\n
        {examples}\n
        '''

        prompt_prefix = 'Your task is to create a chain of thought explaining these example codes, so that it can be used to further guide coders to create best QASM to solve the problem. Please only provide the chain of thought process, nothing else'

        prompt = template + prompt_prefix
        analysis = self.llm.generate(prompt, role="prompt", max_tokens=1024)

        return examples, analysis, algo_name


    def generate_coding_prompt(self,question=''):
        examples,analysis,algo_name=self.generate_coding_info(question)
        template=f'''
        The quantum algorithm problem is described below:\n
        ### Problem:\n
        {question}\n

        ### Analysis:\n
        {analysis}

        ### Related Example Code:\n
        These QASM example codes might be helpful:\n
        {examples}\n

        Now, generate the code for the question, please only provide the code itself, nothing else
        '''

        return template


# === Test Code ===
if __name__ == "__main__":
    pass

    

    
    
