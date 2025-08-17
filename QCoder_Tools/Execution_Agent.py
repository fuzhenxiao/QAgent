import ast
import io
import sys
import importlib.util
import traceback
from tools import *
from LLM import LLM_model
import signal


class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Execution time exceeded")


class ExecutorAgent_v0:
    def __init__(self, rag):
        self.rag = rag
    def check_code_syntax(self, code_str):
        try:
            ast.parse(code_str)
            return True, None
        except SyntaxError as e:
            return False, str(e)

    def load_tools_module(self, tools_path, module_name='tools_module'):
        spec = importlib.util.spec_from_file_location(module_name, tools_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def execute_plan(self, plan_output):
        report = {
            'algorithm': plan_output['algorithm'],
            'status': 'success',
            'outputs': {},
            'logs': '',
            'errors': ''
        }

        # Step 1: Check code block
        raw_code = plan_output['code']
        if raw_code.startswith('```python'):
            raw_code = raw_code.strip('```python').strip('```').strip()

        is_valid, syntax_error = self.check_code_syntax(raw_code)
        if not is_valid:
            report['status'] = 'failed'
            report['errors'] = f'Syntax error in code: {syntax_error}'
            return report

        # Step 2: Retrieve tool script path via RAG
        tools_path = self.rag.search(f"tools needed for {plan_output['algorithm']} algorithm")[0][0]
        print(tools_path)
        if not tools_path:
            report['status'] = 'failed'
            report['errors'] = f'Could not locate tools script for {plan_output["algorithm"]}'
            return report

        # Step 3: Load module
        try:
            tools_module = self.load_tools_module(tools_path)
            local_vars = vars(tools_module).copy()
        except Exception as e:
            report['status'] = 'failed'
            report['errors'] = f'Failed to load tools module: {str(e)}'
            return report

        # Step 4: Execute code and capture outputs
        buffer = io.StringIO()
        sys_stdout = sys.stdout
        sys.stdout = buffer

        try:
            exec(raw_code, local_vars)
            # exec_output = local_vars.get('qasm_code', None), local_vars.get('test_passed', None), \
            #               local_vars.get('success_rate', None), local_vars.get('oracle_test_output', None)

            # report['outputs'] = {
            #     'qasm_code': exec_output[0],
            #     'test_passed': exec_output[1],
            #     'success_rate': exec_output[2],
            #     'oracle_test_output': exec_output[3]
            # }
        except Exception as e:
            report['status'] = 'failed'
            report['errors'] = f'Execution error: {str(e)}\nTraceback:\n{traceback.format_exc()}'
        finally:
            sys.stdout = sys_stdout
            report['logs'] = buffer.getvalue()
            buffer.close()

        return report

class ExecutorAgent_v1:
    def __init__(self, llm,rag):
        self.rag = rag
        self.llm = llm



    def check_code_syntax(self, code_str):
        try:
            ast.parse(code_str)
            return True, None
        except SyntaxError as e:
            return False, str(e)

    def load_tools_module(self, tools_path, module_name='tools_module'):
        spec = importlib.util.spec_from_file_location(module_name, tools_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def execute_plan(self, plan_output):
        report = {
            'algorithm': plan_output['algorithm'],
            'status': 'success',
            'outputs': {},
            'logs': '',
            'errors': ''
        }

        plan = plan_output['plan']
        raw_code = plan_output['code']
        if raw_code.startswith('```python'):
            raw_code = raw_code.strip('```python').strip('```').strip()


        # Step 2: Check code syntax
        is_valid, syntax_error = self.check_code_syntax(raw_code)
        if not is_valid:
            report['status'] = 'failed'
            report['errors'] = f'Syntax error in code: {syntax_error}'
            return report

        # Step 3: Retrieve tool script path via RAG
        tools_path = self.rag.search(f"tools needed for {plan_output['algorithm']} algorithm")[0][0]
        if not tools_path:
            report['status'] = 'failed'
            report['errors'] = f'Could not locate tools script for {plan_output["algorithm"]}'
            return report

        # Step 4: Load module
        try:
            tools_module = self.load_tools_module(tools_path)
            local_vars = vars(tools_module).copy()
        except Exception as e:
            report['status'] = 'failed'
            report['errors'] = f'Failed to load tools module: {str(e)}'
            return report

        # Step 5: Execute code and capture outputs
        buffer = io.StringIO()
        sys_stdout = sys.stdout
        sys.stdout = buffer


        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(90)  # 60 seconds timeout


        try:
            exec(raw_code, local_vars)
            exec_output = (
                local_vars.get('qasm_code', None),
                local_vars.get('test_passed', None),
                local_vars.get('success_rate', None),
                local_vars.get('oracle_test_output', None)
            )

            report['outputs'] = {
                'qasm_code': exec_output[0],
                'test_passed': exec_output[1],
                'success_rate': exec_output[2],
                'oracle_test_output': exec_output[3]
            }
        except Exception as e:
            report['status'] = 'failed'
            report['errors'] = f'Execution error: {str(e)}\nTraceback:\n{traceback.format_exc()}'
        finally:
            sys.stdout = sys_stdout
            report['logs'] = buffer.getvalue()
            buffer.close()

        return report


import ast
import io
import sys
import importlib.util
import traceback

class ExecutorAgent:
    def __init__(self, llm, rag):
        self.rag = rag
        self.llm = llm

    def check_code_syntax(self, code_str):
        try:
            ast.parse(code_str)
            return True, None
        except Exception as e:
            return False, traceback.format_exc()

    def load_tools_module(self, tools_path, module_name):
        print('MODULE INFO')
        print(tools_path)
        print(module_name)
        print('MODULE INFO END')
        spec = importlib.util.spec_from_file_location(module_name, tools_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def postcheck_with_llm(self, question, report,tool_description):
        system_prompt = """
You are a Python execution report reviewer.
Given the following question and report, decide if the execution was successful.
You do not need to rigorously verify the semantic correctness of the generated QASM code. Instead, your main task is to analyze the generated plan, the corresponding Python code that outputs the QASM, the execution report, and the final output.
Your goal is to determine:
1.Whether the final output is correctly printed as expected.
2.Whether the Python code fulfills the user's intent.
3.Whether the provided tools (i.e., functions) were used appropriately to meet the user’s needs.

Note that:
1. he tools provided are guaranteed to be correct.
2. It is not mandatory to use them, but if they help achieve the goal, they should be used.
3. DO NOT judge based on the semantic correctcness of qasm code.
4. Repeated gates or long circuits are NOT supposed to be the reason for failure!

Focus on evaluating whether the overall process—from plan to code to output—aligns with the user’s intent.

If successful, output:
SUCCESS

If failed, output:
FAILURE: <brief reason>
"""     
        prompt_input = f"<<QUESTION>>\n{question}\n<<END OF QUESTION>>\n<<PROVIDED TOOLS>>\n{tool_description}\n<<END OF PROVIDED TOOLS>>\n<<REPORT>>\n{report}\n<<END OF REPORT>>"
        llm_response = self.llm.generate(system_prompt, prompt_input,max_tokens=200).strip()
        return llm_response

    def execute_plan(self, plan_output):
        report = {
            'algorithm': plan_output['algorithm'],
            'status': 'success',
            'logs': '',
            'errors': '',
            'llm_judgment': 'no comment'
        }

        raw_code = plan_output['code']
        question = plan_output['question']
        print('raw code from exe agent:',raw_code, type(raw_code))

        if raw_code is None:
            report['status'] = 'failed'
            report['errors'] = f'Did not generate code or the code is not correctly detected'
            return report

        if raw_code.startswith('```python'):
            raw_code = raw_code.strip('```python').strip('```').strip()


        forbidden_keywords = ['pip', 'os.', 'subprocess', 'sys.exit', '__import__', 'open(']
        for keyword in forbidden_keywords:
            if keyword in raw_code:
                report['status'] = 'failed'
                report['errors'] = 'Illegal operation trying to modify environment'
                return report
        # Step 1: Check code syntax
        is_valid, syntax_error = self.check_code_syntax(raw_code)
        if not is_valid:
            report['status'] = 'failed'
            report['errors'] = f'Syntax error in code: {syntax_error}'
            return report

        # Step 2: Retrieve and load tools modules for each algorithm
        local_vars = {}
        algo_names = [name.strip() for name in plan_output['algorithm'].split('+')]

        for algo_name in algo_names:
            # tools_path = self.rag.search(f"tools needed for {algo_name} algorithm")[0][0]
            tools_path = f'./tools/{algo_name}_tools.py'
            if not tools_path:
                report['status'] = 'failed'
                report['errors'] = f"Could not locate tools script for {algo_name}"
                return report

            try:
                module = self.load_tools_module(tools_path, module_name=f"{algo_name}_tools")
                local_vars.update(vars(module))
            except Exception as e:
                report['status'] = 'failed'
                report['errors'] = f'Failed to load tools module for {algo_name}: {str(e)}'
                return report

        # Step 3: Execute code and capture outputs
        buffer = io.StringIO()
        sys_stdout = sys.stdout
        sys.stdout = buffer
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(60)  # 60 seconds timeout

        try:
            exec(raw_code, local_vars)
        except TimeoutException:
            report['status'] = 'failed'
            report['errors'] = 'Generated code consumes too much time'
        except Exception as e:
            report['status'] = 'failed'
            report['errors'] = f'Execution error: {str(e)}\nTraceback:\n{traceback.format_exc()}'
        finally:
            signal.alarm(0)
            sys.stdout = sys_stdout
            captured_logs = buffer.getvalue()
            buffer.close()
            report['logs'] = captured_logs

        # Check if logs are empty despite success
        if report['status'] == 'success' and (captured_logs.strip() == '' or captured_logs.strip().lower() == 'none' or captured_logs == None):
            report['status'] = 'failed'
            report['errors'] = 'Execution completed but did not print anything, the output cannot be captured by io buffer'


        # Step 4: Post-check with LLM
        llm_judgment = self.postcheck_with_llm(question, report,plan_output['tools'])
        report['llm_judgment'] = llm_judgment

        return report






if __name__ == "__main__":
    pass