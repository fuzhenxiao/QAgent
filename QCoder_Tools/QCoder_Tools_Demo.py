from tools import *
from Plan_Agent import Plan_Agent
from Execution_Agent import ExecutorAgent
from Reflection_Agent import ReflectionAgent
from LLM import LLM_model
import traceback
import importlib.util
import os
import re

def keep_qasm_lines_only(text):
    """Filters a string to keep only valid OpenQASM 3.0 lines."""
    if not isinstance(text, str):
        return ""
    valid_lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        # This regex checks for common QASM keywords and syntax.
        if (
            stripped.endswith(';') or
            stripped.endswith('{') or
            stripped.endswith('}') or
            re.match(r'^(gate|include|qubit|bit|const|let|def|output|input|OPENQASM)\b', stripped)
        ):
            valid_lines.append(stripped)
    return '\n'.join(valid_lines)

class QCoder(object):

    def __init__(self, llm_choice='', llm_key='', reflection_round=3, temp=None, candidate_num=1,provider='nebius'):
        self.reflection_round = reflection_round
        self.LLM = LLM_model(llm_choice, llm_key, temp,provider=provider)
        self.rag = RAG(root_folder="./QCircuitNet_Dataset-simplified/Algorithm_Design")
        self.plan_agent = Plan_Agent(self.LLM, self.rag)
        self.exe_agent = ExecutorAgent(self.LLM, self.rag)
        self.reflect_agent = ReflectionAgent(self.LLM)
        self.candidate_num = candidate_num

    def generate_with_tools(self, question='', qubit_n=None):
        """
        Executes the plan-execute-reflect loop with multiple candidates and returns all results.
        """
        reports_dict = {}
        codes_dict = {}
        overall_success = False
        
        for cand in range(1, self.candidate_num + 1):
            alloutputs = []
            allerrs = []
            MAX_REFLECTION_ROUNDS = self.reflection_round
            success = False
            
            # --- Initial Attempt (Round 1) ---
            try:
                plan_and_code = self.plan_agent.plan(question, 1000)
                report = self.exe_agent.execute_plan(plan_and_code)
                
                key = f"candidate_{cand}_round_1_{'success' if report['llm_judgment'].startswith('SUCCESS') else 'fail'}"
                reports_dict[key] = report.get('errors', 'No errors reported.')
                codes_dict[key] = keep_qasm_lines_only(report.get('logs', ''))
                
                if report['llm_judgment'].startswith("SUCCESS"):
                    success = True
                    overall_success = True
                    break
                
                # --- Reflection Loop (Rounds 2 to N+1) ---
                for round_idx in range(2, MAX_REFLECTION_ROUNDS + 2):
                    reflection = self.reflect_agent.reflect_and_revise(question, plan_and_code, report)
                    
                    if reflection.get('success'):
                        # Even if reflection agent judges success, we save the last state
                        key = f"candidate_{cand}_round_{round_idx}_success"
                        reports_dict[key] = report.get('errors', 'No errors reported.')
                        codes_dict[key] = keep_qasm_lines_only(report.get('logs', ''))
                        success = True
                        overall_success = True
                        break
                    
                    # Update plan and code from reflection
                    plan_and_code['plan'] = reflection['plan']
                    plan_and_code['code'] = reflection['code']
                    
                    # Re-execute the revised plan
                    report = self.exe_agent.execute_plan(plan_and_code)
                    
                    key = f"candidate_{cand}_round_{round_idx}_{'success' if report['llm_judgment'].startswith('SUCCESS') else 'fail'}"
                    reports_dict[key] = report.get('errors', 'No errors reported.')
                    codes_dict[key] = keep_qasm_lines_only(report.get('logs', ''))
                    
                    if report['llm_judgment'].startswith("SUCCESS"):
                        success = True
                        overall_success = True
                        break
                
                # If this candidate succeeded, don't run further candidates
                if success:
                    break
                    
            except Exception as e:
                key = f"candidate_{cand}_round_1_fail"
                reports_dict[key] = f"Exception: {str(e)}\n{traceback.format_exc()}"
                codes_dict[key] = "// Error during generation"
                break
        
        return overall_success, reports_dict, codes_dict


if __name__ == "__main__":

    nebius_api_key='YOUR OWN API KEY'
    bv_question='''Given a black box function $f: \{0,1\}^n \longmapsto \{0,1\}$. The function is guaranteed to return the bitwise product of the input with a secret string $s \in \{0, 1\}^n$. In other words, given an input $x$, $f(x) = x \cdot s \mod 2$. Please design a quantum algorithm to find $s$. The function is provided as a black-box oracle gate named "Oracle" in the "oracle.inc" file which operates as $O_f \ket{x}\ket{y} = \ket{x}\ket{y\oplus f(x)}$. The input qubits $\ket{x}$ are indexed from $0$ to $n-1$. The output qubit $\ket{y}$ is indexed as qubit $n$. Please provide the following components for the algorithm design with n = 5: 1. the corresponding quantum circuit implementation with QASM without oracle.'''
        # "dj": '''Given a black box function $f: \{0,1\}^n \longmapsto \{0,1\}$. The function is known to be either constant (outputs $0$ for all inputs or $1$ for all inputs) or balanced (outputs $0$ for half of the inputs and  $1$ for the other half). Please design a quantum algorithm to determine whether the given function $f(x)$ is constant or balanced. The function is provided as a black-box oracle gate named "Oracle" in the "oracle.inc" file which operates as $O_f \ket{x}\ket{y} = \ket{x}\ket{y\oplus f(x)}$. The input qubits $\ket{x}$ are indexed from $0$ to $n-1$. The output qubit $\ket{y}$ is indexed as qubit $n$. Please provide the following components for the algorithm design with n = _NUM_: 1. the corresponding quantum circuit implementation with QASM without oracle.''',
        # "grover": '''Consider an unstructured search problem. Given a black box function $f:\{0,1\}^n \rightarrow\{0,1\}$, it is known that there exists a unique marked item $w$ such that $f(w) = 1$, i.e. $f(x) = 1$ if $x = w$, $f(x) = 0$ if $x \neq w$. Please design a quantum algorithm to find $w$. The function is provided as a black-box oracle gate named "Oracle" in the "oracle.inc" file which operates as $O_f\ket{x} = (-1)^{f(x)}\ket{x}$. The input qubits $\ket{x}$ are indexed from $0$ to $n-1$, and the output qubits are indexed from $0$ to $n-1$. Please provide the following components for the algorithm design with n = _NUM_: 1. the corresponding quantum circuit implementation with QASM without oracle.''',
        # "pe": '''Given a black box unitary transformation $U$ and a quantum state $\ket{\psi}$, where $U \ket{\psi} = e^{2\pi i \theta} \ket{\psi}$, please design a quantum algorithm to estimate the phase $\theta$ of the eigenvalue to a precision of $\frac{1}{2^n}$. Specifically, we consider $1$-qubit quantum state $\ket{\psi}$ which can be prepared from a gate named "Psi" from $\ket{0}$. You are provided with a controlled-$U$ gate named "CU_0" where the first qubit is control qubit, and the second qubit is target qubit. You can use "CU_0" as a standard two-qubit gate like "CU_0 q[0], q[1]". The gates "Psi" and "CU_0" are provided in the "oracle.inc" file. Please provide the following components for the algorithm design with n = _NUM_: 1. the corresponding quantum circuit implementation with QASM without oracle.''',
        # "w_state": '''The W State is a quantum superposition with equal expansion coefficients of all possible pure states in which exactly one of the qubits is in the excited state $\ket{1}$ while all other ones are in the ground state $\ket{0}$. For a system with $n$ qubits, the W state is defined as $\ket{\mathrm{W}}=\frac{1}{\sqrt{n}}(\ket{100 \ldots 0}+\ket{010 \ldots 0}+\ldots+\ket{00 \ldots 01})$. Please design a quantum algorithm to prepare the W state. Please provide the following components for the algorithm design with n = _NUM_: 1. the corresponding quantum circuit implementation with QASM without oracle.''',

    
    Q = QCoder(llm_choice='Qwen/Qwen2.5-Coder-32B-Instruct', llm_key=nebius_api_key, reflection_round=3, temp=1.0, candidate_num=1,provider='nebius')
    success, reports_dict, codes_dict = Q.generate_with_tools(question=bv_question, qubit_n=5) 
    print(reports_dict)
    print(codes_dict)
    # for the first run, the RAG module will take a while to generate a dataset-index table
    # You can omit qubit_n, QCoder will analyze required qubit number automatically.