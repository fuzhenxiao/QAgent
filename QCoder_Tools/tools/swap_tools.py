# tools needed for swap algorithm
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.random import random_circuit
from qiskit.qasm3 import dump
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector
from io import StringIO
import re
def create_random_state(n):
    """Create two random n-qubit states and return as gates and statevectors."""
    psi_circuit = random_circuit(n, min(n, 10), max_operands=2)
    phi_circuit = random_circuit(n, min(n, 10), max_operands=2)
    psi_gate = psi_circuit.to_gate()
    phi_gate = phi_circuit.to_gate()
    psi_gate.name = "Psi"
    phi_gate.name = "Phi"
    psi_vec = Statevector(psi_circuit)
    phi_vec = Statevector(phi_circuit)
    return psi_gate, phi_gate, psi_vec, phi_vec

def compute_overlap(psi_vec, phi_vec):
    """Compute the squared overlap between two statevectors."""
    return np.abs(psi_vec.inner(phi_vec)) ** 2


def substract_oracle_from_swap_qasm(qasm_str):
    keep_gates = {'GH', 'IGH'}
    all_gate_pattern = r'gate\s+(\w+)\s*[\s\S]*?\}'
    matches = list(re.finditer(all_gate_pattern, qasm_str))
    for match in matches:
        gate_name = match.group(1)
        if gate_name not in keep_gates:
            qasm_str = qasm_str.replace(match.group(0), '')

    if 'include "oracle.inc";' not in qasm_str:
        qasm_str = re.sub(
            r'(include\s+"stdgates\.inc";)',
            r'\1\ninclude "oracle.inc";',
            qasm_str
        )

    qasm_str = re.sub(r'\n\s*\n', '\n', qasm_str).strip()

    return qasm_str

def generate_swap_test_circuit(n, psi_gate, phi_gate):
    """Generate the swap test circuit for n-qubit states."""
    circuit = QuantumCircuit(2 * n + 1, 1)
    circuit.append(psi_gate, range(n))
    circuit.append(phi_gate, range(n, 2 * n))
    ancilla = 2 * n
    circuit.h(ancilla)
    for i in range(n):
        circuit.cswap(ancilla, i, i + n)
    circuit.h(ancilla)
    circuit.measure(ancilla, 0)
    return circuit

def circuit_to_qasm_string(circuit):
    """Convert a QuantumCircuit to QASM string."""
    buf = StringIO()
    dump(circuit, buf)
    return buf.getvalue()

def run_swap_test_and_get_overlap(circuit, shots=10000):
    """Run the swap test circuit and estimate the overlap."""
    aer_sim = AerSimulator()
    circ = transpile(circuit, aer_sim)
    result = aer_sim.run(circ, shots=int(shots)).result()
    counts = result.get_counts()
    prob_zero = counts.get('0', 0) / shots
    estimated_overlap = max((2 * prob_zero - 1), 0)
    return estimated_overlap

def extract_qubit_groups(n):
    """Return the indices of the psi qubits, phi qubits, and ancilla qubit."""
    psi_qubits = list(range(n))
    phi_qubits = list(range(n, 2 * n))
    ancilla = 2 * n
    return psi_qubits, phi_qubits, ancilla

if __name__ == "__main__":
    n = 4
    psi_gate, phi_gate, psi_vec, phi_vec = create_random_state(n)
    true_overlap = compute_overlap(psi_vec, phi_vec)
    print(f"True overlap: {true_overlap}")

    swap_circuit = generate_swap_test_circuit(n, psi_gate, phi_gate)
    qasm_str = circuit_to_qasm_string(swap_circuit)
    print("Generated QASM:")
    print(substract_oracle_from_swap_qasm(qasm_str))

    estimated_overlap = run_swap_test_and_get_overlap(swap_circuit, shots=10000)
    print(f"Estimated overlap from swap test: {estimated_overlap}")

    psi_qubits, phi_qubits, ancilla = extract_qubit_groups(n)
    print(f"Psi qubits: {psi_qubits}, Phi qubits: {phi_qubits}, Ancilla qubit: {ancilla}")
