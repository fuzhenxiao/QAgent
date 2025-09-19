import random
import re
import math
from qiskit import QuantumCircuit, transpile
from qiskit.qasm3 import loads
from qiskit_aer import AerSimulator

def bernstein_vazirani_oracle(n, secret_string):

    s = secret_string[::-1]
    lines = ["gate Oracle " + ", ".join(f"_gate_q_{i}" for i in range(n + 1)) + " {"]
    for qubit in range(n):
        if s[qubit] == "1":
            lines.append(f"  cx _gate_q_{qubit}, _gate_q_{n};")
    lines.append("}")
    return "\n".join(lines)

def plug_in_oracle(qasm_code, oracle_def):
    pos = qasm_code.find('include "oracle.inc";')
    if pos == -1:
        return None
    return qasm_code[:pos] + oracle_def + qasm_code[pos + len('include "oracle.inc";'):]

def verify_qasm_syntax(qasm_code):
    try:
        return loads(qasm_code),'syntax correct'
    except Exception as e:
        print("QASM parsing failed:", e)
        return None,str(f'"QASM parsing failed. {e}')

def run_and_analyze(circuit, aer_sim):
    circ = transpile(circuit, aer_sim)
    result = aer_sim.run(circ, shots=1).result()
    counts = result.get_counts()
    return list(counts.keys())[0]

def get_secret_strings(n, max_tests=64):

    return list({format(random.randint(0, 2**n - 1), f"0{n}b") for _ in range(max_tests)})


def universal_check(naked_qasm, n):
    test_num=3
    secret_strings = get_secret_strings(n, test_num)
    simulator = AerSimulator()
    total = len(secret_strings)
    correct = 0

    for secret_string in secret_strings:
        oracle_def = bernstein_vazirani_oracle(n, secret_string)
        full_qasm = plug_in_oracle(naked_qasm, oracle_def)
        if full_qasm is None:
            return False, 0, 'missing: include "oracle.inc"; '


        circuit,report = verify_qasm_syntax(full_qasm)
        if circuit is None:
            return False, 0, report 

        prediction = run_and_analyze(circuit, simulator)
        if prediction == secret_string:
            correct += 1
        else:
            pass

    accuracy = correct / total
    if correct == total:
        return True, 1, 'passed all tests'
    else:
        return False, accuracy, 'failed some tests'


# Example usage
naked_qasm = '''
OPENQASM 3.0;
include "stdgates.inc";
include "oracle.inc";
bit[4] c;
qubit[5] q;
h q[0];
h q[1];
h q[2];
h q[3];
x q[4];
h q[4];
Oracle q[0], q[1], q[2], q[3], q[4];
h q[0];
h q[1];
h q[2];
h q[3];
c[0] = measure q[0];
c[1] = measure q[1];
c[2] = measure q[2];
c[3] = measure q[3];
'''

# # Run the evaluation
universal_check(naked_qasm,4)
