import random
import re
from io import StringIO
from qiskit import QuantumCircuit, transpile
from qiskit.qasm3 import dump, loads
from qiskit_aer import AerSimulator
import math
import traceback



def plug_in_oracle(qasm_code, oracle_def):
    oracle_pos = qasm_code.find('include "oracle.inc";')
    if oracle_pos == -1:
        return None
    return (
        qasm_code[:oracle_pos] + oracle_def + qasm_code[oracle_pos + len('include "oracle.inc";') :]
    )

def verify_qasm_syntax(qasm_code):
    try:
        return loads(qasm_code),'syntax correct'
    except Exception as e:
        print("QASM parsing failed:", e)
        return None,str(f'"QASM parsing failed. {e}')

def circuit_to_qasm_str(circuit):
    buf = StringIO()
    dump(circuit, buf)
    return buf.getvalue()


def create_grover_oracle(n, marked_state):
    oracle = QuantumCircuit(n)
    rev_target = marked_state[::-1]
    zero_inds = [ind for ind, char in enumerate(rev_target) if char == "0"]

    if zero_inds:
        oracle.x(zero_inds)
    oracle.h(n - 1)
    oracle.mcx(list(range(n - 1)), n - 1)
    oracle.h(n - 1)
    if zero_inds:
        oracle.x(zero_inds)

    oracle_gate = oracle.to_gate()
    oracle_gate.name = "Oracle"
    return oracle_gate

def diffusion_operator(n):
    diffuser = QuantumCircuit(n)
    diffuser.h(range(n))
    diffuser.x(range(n))

    diffuser.h(n - 1)
    diffuser.mcx(list(range(n - 1)), n - 1)
    diffuser.h(n - 1)

    diffuser.x(range(n))
    diffuser.h(range(n))

    diffuser_gate = diffuser.to_gate()
    diffuser_gate.name = "Diffuser"
    return diffuser_gate



def grover_circuit(n, oracle_gate):
    num_iterations = math.floor(math.pi / 4 * math.sqrt(2 ** n))
    circuit = QuantumCircuit(n, n)

    circuit.h(range(n))
    diffuser = diffusion_operator(n)

    for _ in range(num_iterations):
        circuit.append(oracle_gate, range(n))
        circuit.append(diffuser, range(n))

    circuit.measure(range(n), range(n))
    return circuit

def run_and_analyze(circuit, aer_sim, shots=100):
    circ = transpile(circuit, aer_sim)
    result = aer_sim.run(circ, shots=shots).result()
    counts = result.get_counts()
    return max(counts, key=counts.get)



def universal_check(naked_qasm, n, test_num=10, verbose=False):

    aer_sim = AerSimulator()

    all_states = [format(i, f"0{n}b") for i in range(2 ** n)]
    
    success_count = 0

    if n > 7:
        all_states = random.sample(all_states, 3)  
    else:
        all_states = random.sample(all_states, 5)

    total = len(all_states)

    for marked_state in all_states:
        oracle_gate = create_grover_oracle(n, marked_state)
        oracle_circ = QuantumCircuit(n)
        oracle_circ.append(oracle_gate, range(n))
        oracle_qasm_str = circuit_to_qasm_str(oracle_circ)

        gate_defs = re.findall(r"(gate [\s\S]+?^\})", oracle_qasm_str, re.MULTILINE)
        oracle_def = "\n\n".join(gate_defs)

        full_qasm = plug_in_oracle(naked_qasm, oracle_def)
        if full_qasm is None:
            return False, 0, 'missing: include "oracle.inc"; '

        if verbose:
            print(f"Marked State: {marked_state}")
            print(full_qasm)

        circuit, msg = verify_qasm_syntax(full_qasm)
        if circuit is None:
            return False, 0, msg

        prediction = run_and_analyze(circuit.copy(), aer_sim)
        if prediction == marked_state:
            success_count += 1
        else:
            pass

    if success_count == total:
        return True, 1, "passed all tests"
    else:
        return False, success_count / total, "failed some tests"



if __name__ == "__main__":
    naked_qasm = """OPENQASM 3.0;
include \"stdgates.inc\";
include \"oracle.inc\";
gate Diffuser _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3 {
  h _gate_q_0;
  h _gate_q_1;
  h _gate_q_2;
  h _gate_q_3;
  x _gate_q_0;
  x _gate_q_1;
  x _gate_q_2;
  x _gate_q_3;
  h _gate_q_3;
  mcx _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3;
  h _gate_q_3;
  x _gate_q_0;
  x _gate_q_1;
  x _gate_q_2;
  x _gate_q_3;
  h _gate_q_0;
  h _gate_q_1;
  h _gate_q_2;
  h _gate_q_3;
}
bit[4] c;
qubit[4] q;
h q[0];
h q[1];
h q[2];
h q[3];
Oracle q[0], q[1], q[2], q[3];
Diffuser q[0], q[1], q[2], q[3];
Oracle q[0], q[1], q[2], q[3];
Diffuser q[0], q[1], q[2], q[3];
c[0] = measure q[0];
c[1] = measure q[1];
c[2] = measure q[2];
c[3] = measure q[3];
"""

    if universal_check_grover(naked_qasm, n=4, test_num=5,verbose=False):
        print("Grover QASM implementation is valid!")
    else:
        print("Grover QASM implementation is invalid.")