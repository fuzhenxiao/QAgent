import os
import re
import glob
import math
import argparse
import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.circuit.library import PhaseGate
from qiskit.qasm3 import dump


import math
import random
from qiskit import QuantumCircuit
from qiskit.circuit.library import PhaseGate
from qiskit_aer import AerSimulator
from qiskit.qasm3 import loads
from qiskit import transpile

def inverse_qft(n):

    circuit = QuantumCircuit(n)

    for qubit in range(n // 2):
        circuit.swap(qubit, n - qubit - 1)

    for target_qubit in range(n):
        for control_qubit in range(target_qubit):
            circuit.cp(
                -np.pi / 2 ** (target_qubit - control_qubit),
                control_qubit,
                target_qubit,
            )
        circuit.h(target_qubit)

    iqft_gate = circuit.to_gate()
    iqft_gate.name = "IQFT"

    return iqft_gate


def quantum_phase_estimation_circuit(n, cu_gate, psi_gate):

    qpe_circuit = QuantumCircuit(n + 1, n)

    qpe_circuit.append(psi_gate, [n])

    qpe_circuit.h(range(n))

    repetitions = 1
    for counting_qubit in range(n):
        for _ in range(repetitions):
            qpe_circuit.append(cu_gate, [counting_qubit, n])
        repetitions *= 2

    qpe_circuit.append(inverse_qft(n), range(n))

    qpe_circuit.measure(range(n), range(n))

    return qpe_circuit


def plug_in_oracle(qasm_code, oracle_def):
    oracle_pos = qasm_code.find('include "oracle.inc";')
    if oracle_pos == -1:
        return None
    return (
        qasm_code[:oracle_pos]
        + oracle_def
        + qasm_code[oracle_pos + len('include "oracle.inc";') :]
    )


def verify_qasm_syntax(qasm_code):
    try:
        return loads(qasm_code),'syntax correct'
    except Exception as e:
        print("QASM parsing failed:", e)
        return None,str(f'"QASM parsing failed. {e}')


def run_and_analyze(circuit, aer_sim):
    circ = transpile(circuit, aer_sim)
    result = aer_sim.run(circ, shots=1000).result()
    counts = result.get_counts()

    if not counts:
        return None

    most_common_bitstring = max(counts.items(), key=lambda x: x[1])[0]
    n = len(most_common_bitstring)
    prediction = int(most_common_bitstring, 2) / (2**n)
    return prediction



def create_random_oracle_qasm(theta=None, m=None):

    if theta is None:
        if m is not None:
            k = random.randint(0, 2**m - 1)
            theta = k / (2 ** m)
        else:
            theta = random.random()

    theta_rad = round(theta * 2 * math.pi, 10)

    oracle = f"""
gate Psi _gate_q_0 {{
  x _gate_q_0;
}}

gate CU_0 _gate_q_0, _gate_q_1 {{
  cp({theta_rad}) _gate_q_0, _gate_q_1;
}}
""".strip()

    return oracle, theta



def universal_check(naked_qasm, n, test_num=1, trials_per_oracle=3):


    sim = AerSimulator()
    passed = 0
    failed_cases = []

    for i in range(test_num):
        oracle_def, theta_true = create_random_oracle_qasm(m=n)
        full_qasm = plug_in_oracle(naked_qasm, oracle_def)
        if full_qasm is None:
            return False, 0, 'missing: include oracle.inc; '
        circuit,report = verify_qasm_syntax(full_qasm)
        if circuit is None:
            return False, 0, report 

        measure_count = sum(1 for instr in circuit.data if instr.operation.name == "measure")
        tol = 2 / (2 ** measure_count)

        success_count = 0
        for _ in range(trials_per_oracle):
            theta_pred = run_and_analyze(circuit.copy(), sim)
            if theta_pred is not None and abs(theta_pred - theta_true) <= tol:
                success_count += 1

        if success_count >= (trials_per_oracle // 2 + 1):
            passed += 1
        else:
            failed_cases.append((i, theta_true, success_count))

    pass_ratio = passed / test_num

    if pass_ratio >= 0.5:
        return True, pass_ratio, "passed all tests"
    else:
        return False, pass_ratio, f"failed most tests"



if __name__ == "__main__":
    test_qasm = '''OPENQASM 3.0;
include "stdgates.inc";
include "oracle.inc";
gate CU_1 _gate_q_0, _gate_q_1 {
  pow(2) @ CU_0 _gate_q_0, _gate_q_1;
}
gate CU_2 _gate_q_0, _gate_q_1 {
  pow(2) @ CU_1 _gate_q_0, _gate_q_1;
}
gate CU_3 _gate_q_0, _gate_q_1 {
  pow(2) @ CU_2 _gate_q_0, _gate_q_1;
}
gate IQFT _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3 {
  swap _gate_q_0, _gate_q_3;
  swap _gate_q_1, _gate_q_2;
  h _gate_q_0;
  cp(-pi/2) _gate_q_0, _gate_q_1;
  h _gate_q_1;
  cp(-pi/4) _gate_q_0, _gate_q_2;
  cp(-pi/2) _gate_q_1, _gate_q_2;
  h _gate_q_2;
  cp(-pi/8) _gate_q_0, _gate_q_3;
  cp(-pi/4) _gate_q_1, _gate_q_3;
  cp(-pi/2) _gate_q_2, _gate_q_3;
  h _gate_q_3;
}
bit[4] c;
qubit[5] q;
Psi q[4];
h q[0];
h q[1];
h q[2];
h q[3];
CU_0 q[0], q[4];
CU_1 q[1], q[4];
CU_2 q[2], q[4];
CU_3 q[3], q[4];
IQFT q[0], q[1], q[2], q[3];
c[0] = measure q[0];
c[1] = measure q[1];
c[2] = measure q[2];
c[3] = measure q[3];'''

    passed = universal_check(test_qasm,4)
    print("Result:", "PASS" if passed else "FAIL")
