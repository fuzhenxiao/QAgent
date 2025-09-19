import numpy as np
import argparse
from qiskit import transpile
from qiskit.qasm3 import loads
from qiskit.quantum_info import Statevector, DensityMatrix, partial_trace
from qiskit_aer import AerSimulator


def print_and_save(message, text):
    print(message)
    text.append(message)


def goal_state_vector(n):

    goal_state = np.zeros(2 ** n, dtype=complex)
    for i in range(n):
        goal_state[1 << i] = 1 / np.sqrt(n)
    return Statevector(goal_state)

def goal_state_matrix(n):

    goal_density_matrix = DensityMatrix(goal_state_vector(n))
    return goal_density_matrix


def extract_output_state_matrix(statevector, qubit_indices, num_qubits):
    auxilary_qubits = list(set(range(num_qubits)) - set(qubit_indices))
    auxilary_qubits.sort()
    density_matrix = DensityMatrix(statevector)
    reduced_density_matrix = partial_trace(density_matrix, auxilary_qubits)
    return reduced_density_matrix


def verify_result_matrix(circuit, n, qubit_indices, eps=1e-2):

    aer_sim = AerSimulator(method="statevector")
    circ = circuit.copy()
    circ.save_statevector()
    circ = transpile(circ, aer_sim)
    goal_density_matrix = goal_state_matrix(n)
    result = aer_sim.run(circ).result()
    statevector = result.get_statevector(circ)
    output_density_matrix = extract_output_state_matrix(
        statevector, qubit_indices, circ.num_qubits
    )
    return np.isclose(
        output_density_matrix.data, goal_density_matrix.data, atol=eps
    ).all()


def verify_result_vector(circuit, n, eps=1e-2):

    aer_sim = AerSimulator(method="statevector")
    circ = circuit.copy()
    circ.save_statevector()
    circ = transpile(circ, aer_sim)
    goal_state = goal_state_vector(n)
    result = aer_sim.run(circ).result()
    statevector = result.get_statevector(circ)
    return statevector.equiv(goal_state, rtol=eps)


def verify_qasm_syntax(qasm_str):
    try:
        circuit = loads(qasm_str)
        return circuit, "Syntax is valid."
    except Exception as e:

        return None, str(f'"QASM parsing failed. {e}')



def universal_check(qasm_string, n):

    circuit, report = verify_qasm_syntax(qasm_string)
    if circuit is None:
        return False, 0, report
    try:
        aer_sim = AerSimulator(method="statevector")
    
        qubit_indices = list(range(circuit.num_qubits))
        if verify_result_matrix(circuit, n, qubit_indices):
            return True, 1.0, 'passed all tests'
        else:
            return False, 0.0, 'The W state is inaccurate'
    except Exception as e:
        print(f"An error occurred: {e}")
        return False, 0.0, str(e)

wstate_universal_execute_description = """
universal_execute(qasm_code, n) -> str

Purpose:
  Execute a W-state circuit given in OpenQASM 3.0, measure all n qubits,
  and return the most probable measurement outcome.

Inputs:
  - qasm_code: str
      OpenQASM 3.0 code that prepares an n-qubit W state. Must define
      a qubit register of size n.
  - n: int
      Number of qubits. Must match the circuit's qubit count.

Behavior:
  1) Parse qasm_code and verify the circuit has n qubits.
  2) Add measurements on all qubits (if not present).
  3) Simulate the circuit on AerSimulator with 1024 shots.
  4) Return the most frequent bitstring observed.

Output:
  - winner_state: str
      The n-bit measurement outcome (MSB-left) with the highest probability.

Errors:
  - ValueError on invalid inputs or qubit mismatch.
  - Propagates Qiskit parsing/simulation exceptions.
"""

def universal_execute(qasm_code: str, n: int) -> str:
    from qiskit import QuantumCircuit, ClassicalRegister, transpile
    from qiskit.qasm3 import loads
    from qiskit_aer import AerSimulator


    try:
        circuit = loads(qasm_code)
    except Exception as e:
        raise ValueError(f"QASM parsing failed: {e}")

    if circuit.num_qubits != n:
        raise ValueError(f"Qubit count mismatch: expected {n}, got {circuit.num_qubits}")


    has_measure = any(inst.operation.name == "measure" for inst in circuit.data)
    if not has_measure:
        if not circuit.cregs:
            circuit.add_register(ClassicalRegister(n, "c"))
        circuit.measure(range(n), range(n))

    sim = AerSimulator()
    compiled = transpile(circuit, sim)
    result = sim.run(compiled, shots=1024).result()
    counts = result.get_counts(compiled)

    winner_state = max(counts, key=counts.get)
    return winner_state



if __name__ == "__main__":
    qasm_string = """
        OPENQASM 3.0;
        include "stdgates.inc";
        bit[3] c;
        qubit[3] q;
        x q[2];
        ry(-0.9553166181245093) q[1];
        cz q[2], q[1];
        ry(0.9553166181245093) q[1];
        ry(-pi/4) q[0];
        cz q[1], q[0];
        ry(pi/4) q[0];
        cx q[1], q[2];
        cx q[0], q[1];
        """

    n = 3
    print(universal_check(qasm_string, n))
