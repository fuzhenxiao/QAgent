# tools needed for ghz algorithm
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.qasm3 import dump
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector
from io import StringIO

def generate_ghz_circuit(n):
    """Generate a GHZ state circuit with n qubits."""
    circuit = QuantumCircuit(n)
    circuit.h(0)
    for i in range(1, n):
        circuit.cx(0, i)
    return circuit

def circuit_to_qasm_string(circuit):
    """Convert a QuantumCircuit to QASM string."""
    buf = StringIO()
    dump(circuit, buf)
    return buf.getvalue()

def get_goal_ghz_statevector(n):
    """Return the expected GHZ statevector."""
    state = np.zeros(2 ** n, dtype=complex)
    state[0] = 1 / np.sqrt(2)
    state[-1] = 1 / np.sqrt(2)
    return Statevector(state)

def run_ghz_circuit_and_get_statevector(circuit):
    """Run the GHZ circuit on the statevector simulator and return the result statevector."""
    aer_sim = AerSimulator(method="statevector")
    circ = circuit.copy()
    circ.save_statevector()
    circ = transpile(circ, aer_sim)
    result = aer_sim.run(circ).result()
    statevector = result.get_statevector(circ)
    return statevector

def check_ghz_equivalence(statevector, n, rtol=1e-3):
    """Check if the result statevector is equivalent to the target GHZ statevector."""
    goal_state = get_goal_ghz_statevector(n)
    return statevector.equiv(goal_state, rtol=rtol)

def extract_qubit_indices(circuit):
    """Return the list of qubit indices used in the circuit."""
    return list(range(circuit.num_qubits))

if __name__ == "__main__":
    n = 4
    ghz_circuit = generate_ghz_circuit(n)
    qasm_str = circuit_to_qasm_string(ghz_circuit)
    print("Generated QASM:")
    print(qasm_str)

    statevector = run_ghz_circuit_and_get_statevector(ghz_circuit)
    is_equiv = check_ghz_equivalence(statevector, n)
    print(f"Is the statevector equivalent to GHZ? {is_equiv}")

    qubits = extract_qubit_indices(ghz_circuit)
    print(f"Qubit indices: {qubits}")
