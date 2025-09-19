# tools needed for phase_estimation algorithm
import numpy as np
import math
import re
from qiskit import QuantumCircuit, transpile
from qiskit.qasm3 import dump
from qiskit_aer import AerSimulator
from qiskit.circuit.library import PhaseGate
from io import StringIO
import random
def generate_random_theta_based_on_n(n):
    k = random.randint(1, 2**n - 1)
    theta = (k / 2**n) * 2 * math.pi
    return theta, k / 2**n  # 返回角度和标准化比例

def circuit_to_qasm_str(circuit):
    buf = StringIO()
    dump(circuit, buf)
    return buf.getvalue()

def gate_to_qasm_str(gate):
    circuit=gate.definition
    buf = StringIO()
    dump(circuit, buf)
    return buf.getvalue()


def My_U_gate(theta):
    # u_gate = PhaseGate(theta)
    # cu_gate = u_gate.control(1)
    # cu_gate.name = "CU"
    # return cu_gate
    qc = QuantumCircuit(2)
    qc.cp(theta, 0, 1)
    cu_gate = qc.to_gate()
    cu_gate.name = "CU_0"
    return cu_gate

def My_psi_gate():
    psi_circuit = QuantumCircuit(1)
    psi_circuit.x(0)
    psi_gate = psi_circuit.to_gate()
    psi_gate.name = "Psi"
    return psi_gate


def create_phase_estimation_circuit(n, cu_gate, psi_gate):
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

def substract_oracle_from_phase_estimation_qasm(qasm_str):
    all_gate_pattern = r'gate\s+(\w+)\s*[\s\S]*?\}'
    matches = re.finditer(all_gate_pattern, qasm_str)
    remove_gates = {'Psi', 'CU_0'}
    new_code = qasm_str
    for match in matches:
        gate_name = match.group(1)
        if gate_name in remove_gates:
            gate_block = match.group(0)
            new_code = new_code.replace(gate_block, '')
    #new_code = new_code.replace('CU', 'include "oracle.inc";')
    new_code = re.sub(r'\n\s*\n', '\n', new_code).strip()
    if 'include "oracle.inc";' not in new_code:
        new_code = re.sub(
            r'(include\s+"stdgates\.inc";)',
            r'\1\ninclude "oracle.inc";',
            new_code
        )
    return new_code

def run_phase_estimation_circuit(phase_circuit):
    aer_sim = AerSimulator()
    circ = transpile(phase_circuit, aer_sim)
    result = aer_sim.run(circ, shots=1).result()
    count = result.get_counts()
    y = list(count.keys())[0]
    n = len(y)
    y = int(y, 2)
    prediction = y / (2 ** n)
    return prediction

if __name__ == "__main__":
    n = 5
    theta, theta_fraction = generate_random_theta_based_on_n(n)
    print(f"Using n={n}, theta={theta_fraction} (fraction of full circle)")

    cu_gate = My_U_gate(theta)
    print(gate_to_qasm_str(cu_gate))
    psi_gate=My_psi_gate()
    full_circuit = create_phase_estimation_circuit(n, cu_gate,psi_gate)
    full_circ_qasm = circuit_to_qasm_str(full_circuit)
    without_oracle = substract_oracle_from_phase_estimation_qasm(full_circ_qasm)
    print("QASM without oracle definition:")
    print(without_oracle)

    predicted_phase = run_phase_estimation_circuit(full_circuit)
    print(f"Predicted phase: {predicted_phase}")
    print(f"Expected phase:  {theta_fraction}")
    print(f"Error:           {abs(predicted_phase - theta_fraction)}")
