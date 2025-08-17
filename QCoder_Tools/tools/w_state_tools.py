# tools needed for w_state algorithm
import numpy as np
import math
from qiskit import QuantumCircuit, transpile
from qiskit.qasm3 import dump
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector, DensityMatrix, partial_trace
from io import StringIO

def generate_w_state_circuit(n):
    def F_gate(theta):
        circuit = QuantumCircuit(2)
        circuit.ry(-theta, 1)
        circuit.cz(0, 1)
        circuit.ry(theta, 1)

        F_gate = circuit.to_gate()
        F_gate.name = "F"

        return F_gate


    def create_w_state(n):
        circuit = QuantumCircuit(n, n)
        circuit.x(n - 1)

        for i in range(n - 1):
            circuit.append(
                F_gate(math.acos(math.sqrt(1.0 / (n - i)))),
                [n - 1 - i, n - 2 - i],
            )

        for i in range(n - 1):
            circuit.cx(n - 2 - i, n - 1 - i)

        return circuit

    def F_circuit(circuit, i, j, n, k):
        theta = math.acos(math.sqrt(1.0 / (n - k + 1)))
        circuit.ry(-theta, j)
        circuit.cz(i, j)
        circuit.ry(theta, j)

    circuit = QuantumCircuit(n, n)
    circuit.x(n - 1)
    for i in range(0, n - 1):
        F_circuit(circuit, n - 1 - i, n - 2 - i, n, i + 1)
    for i in range(0, n - 1):
        circuit.cx(n - 2 - i, n - 1 - i)
    return circuit

def circuit_to_qasm_string(circuit):
    """Convert a QuantumCircuit to QASM string."""
    buf = StringIO()
    dump(circuit, buf)
    return buf.getvalue()

def run_w_state_and_get_statevector(circuit):
    """Run the W state circuit on statevector simulator and return the statevector."""
    aer_sim = AerSimulator(method="statevector")
    circ = circuit.copy()
    circ.save_statevector()
    circ = transpile(circ, aer_sim)
    result = aer_sim.run(circ).result()
    statevector = result.get_statevector(circ)
    return statevector

def generate_goal_w_statevector(n):
    """Generate the ideal W statevector for n qubits."""
    goal_state = np.zeros(2 ** n, dtype=complex)
    for i in range(n):
        goal_state[1 << i] = 1 / np.sqrt(n)
    return Statevector(goal_state)

def compare_statevectors(statevector, goal_state, rtol=1e-3):
    """Check if two statevectors are equivalent up to tolerance."""
    return statevector.equiv(goal_state, rtol=rtol)

def extract_qubit_indices(n):
    """Return the list of qubit indices involved in the W state circuit."""
    return list(range(n))

if __name__ == "__main__":
    n = 4
    w_circuit = generate_w_state_circuit(n)
    qasm_str = circuit_to_qasm_string(w_circuit)
    print("Generated QASM:")
    print(qasm_str)

    statevector = run_w_state_and_get_statevector(w_circuit)
    goal_state = generate_goal_w_statevector(n)
    is_equiv = compare_statevectors(statevector, goal_state)
    print(f"Is the circuit's statevector equivalent to the ideal W state? {is_equiv}")

    qubit_indices = extract_qubit_indices(n)
    print(f"Qubit indices in circuit: {qubit_indices}")
