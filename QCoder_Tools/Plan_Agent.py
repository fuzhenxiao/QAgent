from LLM import LLM_model
import os
import glob
import re
import ast
import yaml
import importlib

def extract_plan(text):
    start = text.find("<<THE PLAN>>")
    end = text.find("<<END OF PLAN>>")
    if start != -1 and end != -1:
        return text[start + len("<<THE PLAN>>"):end].strip()
    else:
        return None

def extract_code(text):
    start = text.find("<<THE CODE>>")
    end = text.find("<<END OF CODE>>")
    if start != -1 and end != -1:
        return text[start + len("<<THE CODE>>"):end].strip()
    else:
        return None


def load_algorithm_tools(algorithm_names):
    tool_descriptions = ""
    for algo in algorithm_names:
        try:
            module_name = f"{algo}_tools_description"
            module = importlib.import_module(module_name)
            data = getattr(module, f"{algo}_tools_description")
        except (ModuleNotFoundError, AttributeError) as e:
            raise ValueError(f"No tool description available for {algo}") from e
        
        for func in data['functions']:
            tool_descriptions += f"- {func['name']}{func['signature']}\n  {func['description']}\n\n"
    return tool_descriptions




class Plan_Agent(object):

    def __init__(self, llm,rag):
        self.llm = llm
        self.rag=rag

    def identify_algorithm(self, question):
        related_results = self.rag.search(question + ',description', top_k=5)
        algo_names = set()

        for related_path, score in related_results:
            #print(related_path, score)
            if score < 0.5:              #
                parts = related_path.split(os.sep)
                algo_name = parts[4].lower()
                algo_names.add(algo_name)

        if algo_names:
            print(f"[RAG identified algorithms]: {list(algo_names)}")
            #return list(algo_names)
        else:
            system_prompt = """
            You are an expert in quantum computing. Given a user’s request, identify which quantum algorithms are needed.
            Output the **algorithm names** (separated by +), nothing else.
            for example: Grover + Simon
            another example: deutsch_jozsa
            Known algorithms include (but are not limited to): Grover, Simon, Bernstein_Vazirani, deutsch_jozsa, simon_multi, simon_ternary, phase_estimation, qft, ghz, qrng, swap, w_state.
            """
            #algo_names = self.llm.generate(question, system_prompt, max_tokens=50).strip().lower().split('+')
            algo_names = self.llm.generate(question+system_prompt, system_prompt, max_tokens=50).strip().lower().split('+')  #this is for llama only
            algo_names = set(name.strip() for name in algo_names)
            print(f"[LLM identified algorithms]: {list(algo_names)}")
            #return algo_names
        if 'simon' in algo_names:
            if 'simon_multi' in algo_names:
                algo_names.discard('simon')
            elif 'simon_ternary' in algo_names:
                algo_names.discard('simon')

        return list(algo_names)

    def plan(self, question='', max_plan_length=500):
        algorithm_names = self.identify_algorithm(question)
        tools_description = load_algorithm_tools(algorithm_names)

        # Step 3: Compose system prompt
        system_prompt = f'''
You are an intelligent Python agent equipped with a set of pre-defined Python functions (all related to certain quantum algorithms).
Your job is to solve the user’s task by calling the appropriate functions with correct arguments, based on the provided function documentation and user instructions.
You must only use the available functions to complete the task—do not write or invent new code.
Do not import Gate from qiskit! it is not supported in older version!
When responding, do not explain or describe the code—simply determine the correct function(s) to call and generate the Python code that completes the task.
If multiple steps are required, chain function calls logically.

Available functions:
{tools_description}

Always assume the functions behave as described. Your goal is to make a plan using these tools, and always try to use existing functions to ensure correctness.
There is no need to import any library, do not import anything in code section. Mind the identation. (You don't need to import anything from qiskit, necessary libraries are all included while loading tools.)
Always perform test functions chosen from the tools if possible, to make sure the code you generated are correct.
You may use fake oracles to create full circuits if the user already provided one but omits details.
In most cases, you don't need to write circuits by yourself, all circuit-generating methods should be provided by tools.
Follow this format, include all information within it, in code section, print the output that the user desires so that it can be easily captured by io stream. for example, if user wants the qasm code, then print the code:

<<THE PLAN>>
describe your plan in steps
<<END OF PLAN>>

<<THE CODE>>
python code 
<<END OF CODE>>
'''

# =================PROMPT OPTION 2===============


#         system_prompt = f'''
# You are an intelligent Python agent equipped with a set of pre-defined Python functions (all related to certain quantum algorithms).
# Your job is to solve the user’s task by calling the appropriate functions with correct arguments, based on the provided function documentation and user instructions.
# please try to use provided existing functions.

# Available functions:
# {tools_description}

# Follow this format, include all information within it, in code section, print the output that the user desires so that it can be easily captured by io stream. for example, if user wants the qasm code, then print the code:

# <<THE PLAN>>
# describe your plan in steps
# <<END OF PLAN>>

# <<THE CODE>>
# python code 
# <<END OF CODE>>
# '''

        # Step 4: Call LLM for plan and code
        txt = self.llm.generate(question, system_prompt, max_plan_length)
        #print('?????',txt)

        # Step 5: Extract sections
        plan = extract_plan(txt)
        code = extract_code(txt)

        plan_agent_out = {
            'question':question,
            'algorithm': '+'.join(algorithm_names),
            'tools':tools_description,
            'plan': plan,
            'code': code,
        }

        return plan_agent_out



# === Test Code ===
if __name__ == "__main__":
    pass
    

    
    
