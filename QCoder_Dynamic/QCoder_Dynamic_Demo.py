from tools import *
from RAG_Agent import RAG_Agent
from Reflection_Agent import Reflection_Agent
from Prompt_Agent import Prompt_Agent
from Coding_Agent import Coding_Agent
from Test_Agent import Test_Agent
from LLM import LLM_model
import traceback
import importlib.util
import os

def load_function_from_script(script_path, function_name):
    module_name = os.path.splitext(os.path.basename(script_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, function_name)

def clean_output(code):
    code=code.replace("```","")
    index = code.find("OPENQASM")
    if index != -1:
        return code[index:]
    else:
        return code

class QCoder(object):
    def __init__(self, llm_choice='', llm_key='', reflection_round=3, temp=None, candidate_num=1,provider='nebius'):
        self.totalround = reflection_round + 1
        self.LLM = LLM_model(llm_choice, llm_key, temp=temp,provider=provider)
        self.internet = None
        self.rag = RAG(root_folder="./QCircuitNet_Dataset-simplified")
        self.coding_agent = Coding_Agent(self.LLM)
        self.reflection_agent = Reflection_Agent(self.LLM, self.internet)
        self.test_agent = Test_Agent(self.LLM, self.rag)
        self.prompt_agent = Prompt_Agent(self.LLM, self.rag)
        self.candidate_num = candidate_num

    def generate_with_reflection(self, use_internet=False, question='', qubit_n=None):
        universal_reports_dict = {}
        codes_dict = {}
        test_script_path = None
        universal_check = None
        overall_success = False
        for cand in range(1, self.candidate_num + 1):
            codes = []
            reports = []
            last_report = ''
            last_qasm_code = ''
            success = False
            for i in range(1, 1 + self.totalround):
                try:
                    if i == 1:
                        if qubit_n is None:
                            qubit_n, test_script_path = self.test_agent.get_n_and_test_script(question)
                        else:
                            _, test_script_path = self.test_agent.get_n_and_test_script(question)
                        examples, analysis, algo_name = self.prompt_agent.generate_coding_info(question, question_n=qubit_n)
                        qasm_code, init_template = self.coding_agent.generate_code(question, examples, analysis)
                        qasm_code = clean_output(qasm_code)
                        self.coding_agent.last_generated_code = qasm_code
                        universal_check = load_function_from_script(test_script_path, 'universal_check')
                    else:
                        qasm_code = self.coding_agent.regenerate_code(init_template, codes, reports)
                        #qubit_n, test_script_path = self.test_agent.get_n_and_test_script(question)
                        qasm_code = clean_output(qasm_code)
                        self.coding_agent.last_generated_code = qasm_code
                    codes.append(qasm_code)
                    issuccess, rate, report = universal_check(qasm_code, qubit_n)
                    reports.append(report)
                    
                    last_report = report
                    last_qasm_code = qasm_code
                    reflection = self.reflection_agent.generate_reflection(init_template, codes, reports)
                    reports[-1] += '\nAnalysis:\n' + reflection
                    key = f"candidate_{cand}_round_{i}_{'success' if issuccess else 'fail'}"
                    universal_reports_dict[key]=report

                    codes_dict[key] = codes[-1]
                    if issuccess:
                        success = True
                        overall_success = True
                        break
                except Exception as e:
                    key = f"candidate_{cand}_round_{i}_fail"
                    universal_reports_dict[key] = f"Exception: {str(e)}\n{traceback.format_exc()}"
                    codes_dict[key] = "// Error during generation"
                    break
            # If a candidate succeeded, do not run further candidates
            if success:
                break
        return overall_success, universal_reports_dict, codes_dict


if __name__ == "__main__":

    bv_question='''Given a black box function $f: \{0,1\}^n \longmapsto \{0,1\}$. The function is guaranteed to return the bitwise product of the input with a secret string $s \in \{0, 1\}^n$. In other words, given an input $x$, $f(x) = x \cdot s \mod 2$. Please design a quantum algorithm to find $s$. The function is provided as a black-box oracle gate named "Oracle" in the "oracle.inc" file which operates as $O_f \ket{x}\ket{y} = \ket{x}\ket{y\oplus f(x)}$. The input qubits $\ket{x}$ are indexed from $0$ to $n-1$. The output qubit $\ket{y}$ is indexed as qubit $n$. Please provide the following components for the algorithm design with n = 5: 1. the corresponding quantum circuit implementation with QASM without oracle.'''
        # "dj": '''Given a black box function $f: \{0,1\}^n \longmapsto \{0,1\}$. The function is known to be either constant (outputs $0$ for all inputs or $1$ for all inputs) or balanced (outputs $0$ for half of the inputs and  $1$ for the other half). Please design a quantum algorithm to determine whether the given function $f(x)$ is constant or balanced. The function is provided as a black-box oracle gate named "Oracle" in the "oracle.inc" file which operates as $O_f \ket{x}\ket{y} = \ket{x}\ket{y\oplus f(x)}$. The input qubits $\ket{x}$ are indexed from $0$ to $n-1$. The output qubit $\ket{y}$ is indexed as qubit $n$. Please provide the following components for the algorithm design with n = _NUM_: 1. the corresponding quantum circuit implementation with QASM without oracle.''',
        # "grover": '''Consider an unstructured search problem. Given a black box function $f:\{0,1\}^n \rightarrow\{0,1\}$, it is known that there exists a unique marked item $w$ such that $f(w) = 1$, i.e. $f(x) = 1$ if $x = w$, $f(x) = 0$ if $x \neq w$. Please design a quantum algorithm to find $w$. The function is provided as a black-box oracle gate named "Oracle" in the "oracle.inc" file which operates as $O_f\ket{x} = (-1)^{f(x)}\ket{x}$. The input qubits $\ket{x}$ are indexed from $0$ to $n-1$, and the output qubits are indexed from $0$ to $n-1$. Please provide the following components for the algorithm design with n = _NUM_: 1. the corresponding quantum circuit implementation with QASM without oracle.''',
        # "pe": '''Given a black box unitary transformation $U$ and a quantum state $\ket{\psi}$, where $U \ket{\psi} = e^{2\pi i \theta} \ket{\psi}$, please design a quantum algorithm to estimate the phase $\theta$ of the eigenvalue to a precision of $\frac{1}{2^n}$. Specifically, we consider $1$-qubit quantum state $\ket{\psi}$ which can be prepared from a gate named "Psi" from $\ket{0}$. You are provided with a controlled-$U$ gate named "CU_0" where the first qubit is control qubit, and the second qubit is target qubit. You can use "CU_0" as a standard two-qubit gate like "CU_0 q[0], q[1]". The gates "Psi" and "CU_0" are provided in the "oracle.inc" file. Please provide the following components for the algorithm design with n = _NUM_: 1. the corresponding quantum circuit implementation with QASM without oracle.''',
        # "w_state": '''The W State is a quantum superposition with equal expansion coefficients of all possible pure states in which exactly one of the qubits is in the excited state $\ket{1}$ while all other ones are in the ground state $\ket{0}$. For a system with $n$ qubits, the W state is defined as $\ket{\mathrm{W}}=\frac{1}{\sqrt{n}}(\ket{100 \ldots 0}+\ket{010 \ldots 0}+\ldots+\ket{00 \ldots 01})$. Please design a quantum algorithm to prepare the W state. Please provide the following components for the algorithm design with n = _NUM_: 1. the corresponding quantum circuit implementation with QASM without oracle.''',

    candidate_num = 1
    reflection_num = 3
    temp = 1.0
    trial=2

    nebius_api_key='YOUR OWN API KEY'
    Q = QCoder(llm_choice='Qwen/Qwen2.5-Coder-32B-Instruct', llm_key=nebius_api_key, reflection_round=3, temp=1.0, candidate_num=1,provider='nebius')
    success, reports_dict, codes_dict = Q.generate_with_reflection(question=bv_question, qubit_n=5) 
    print(reports_dict)
    print(codes_dict)

    # for the first run, the RAG module will take a while to generate a dataset-index table
    # You can omit qubit_n, QCoder will analyze required qubit number automatically.