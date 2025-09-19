import random
import re
from qiskit import QuantumCircuit, transpile
from qiskit.qasm3 import loads
from qiskit_aer import AerSimulator


def deutsch_jozsa_oracle_qasm(n, is_constant, key_string):
    lines = ["gate Oracle " + ", ".join(f"_gate_q_{i}" for i in range(n + 1)) + " {"]
    if is_constant:
        if key_string[-1] == "1":
            lines.append(f"  x _gate_q_{n};")
        else:
            lines.append(f"  id _gate_q_{n};")
    else:
        for i in range(n):
            if key_string[i] == "1":
                lines.append(f"  x _gate_q_{i};")
        for i in range(n):
            lines.append(f"  cx _gate_q_{i}, _gate_q_{n};")
        for i in range(n):
            if key_string[i] == "1":
                lines.append(f"  x _gate_q_{i};")
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
    key = list(counts.keys())[0]
    return "balanced" if "1" in key else "constant"


def get_secret_strings(n, max_tests=64):

    return list({format(random.randint(0, 2**n - 1), f"0{n}b") for _ in range(max_tests)})


def universal_check(naked_qasm,n):
    import re
    from qiskit_aer import AerSimulator
    test_num=3
    simulator = AerSimulator()
    correct = 0
    total = 0


    for bit in ["0", "1"]:
        oracle_def = deutsch_jozsa_oracle_qasm(n, True, bit)
        full_qasm = plug_in_oracle(naked_qasm, oracle_def)
        if full_qasm is None:
            return False, 0, 'missing: include "oracle.inc"; '
        circuit,rep = verify_qasm_syntax(full_qasm)
        if circuit is None:
            return False, 0, rep
        prediction = run_and_analyze(circuit, simulator)
        if prediction == "constant":
            correct += 1
        else:
            pass
        total += 1

    for secret in get_secret_strings(n, test_num):
        oracle_def = deutsch_jozsa_oracle_qasm(n, False, secret)
        full_qasm = plug_in_oracle(naked_qasm, oracle_def)
        circuit,rep= verify_qasm_syntax(full_qasm)
        if circuit is None:
            return False, 0, rep
        prediction = run_and_analyze(circuit, simulator)
        if prediction == "balanced":
            correct += 1
        else:
            pass
        total += 1

    accuracy = correct / total
    if correct == total:
        return True, 1, 'passed all tests'
    else:
        return False, accuracy, 'failed some tests'


