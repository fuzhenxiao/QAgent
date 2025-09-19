import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.qasm3 import loads
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector
from typing import Tuple

def get_goal_ghz_statevector(n):
    state = np.zeros(2 ** n, dtype=complex)
    state[0] = 1 / np.sqrt(2)
    state[-1] = 1 / np.sqrt(2)
    return Statevector(state)

def run_circuit_and_get_statevector(circuit):

    sim = AerSimulator(method="statevector")
    circuit.save_statevector()
    compiled = transpile(circuit, sim)
    result = sim.run(compiled).result()
    return result.get_statevector(compiled)

def universal_check(qasm: str, n: int, trials: int = 1) -> Tuple[bool, float, str]:

    try:
        circuit = loads(qasm)
    except Exception as e:
        return False, 0.0, f"QASM parsing failed: {str(e)}"

    if circuit.num_qubits != n:
        return False, 0.0, f"Qubit count mismatch: expected {n}, got {circuit.num_qubits}"

    try:
        statevector = run_circuit_and_get_statevector(circuit)
    except Exception as e:
        return False, 0.0, f"Simulation failed: {str(e)}"

    try:
        goal = get_goal_ghz_statevector(n)
        is_equiv = statevector.equiv(goal, rtol=1e-3)
        success_rate = 1.0 if is_equiv else 0.0
        return is_equiv, success_rate, f"passed all tests"
    except Exception as e:
        return False, 0.0, f"Equivalence check failed: {str(e)}"



universal_execute_description = """
universal_execute(qasm: str, n: int) -> winner_state: str

Purpose:
  Execute a GHZ-state circuit given in OpenQASM 3.0, measure all n qubits,
  and return the bitstring with the highest observed probability along with
  its empirical probability.

Inputs:
  - qasm: str
      OpenQASM 3.0 source that prepares an n-qubit GHZ state (or any n-qubit
      state you’d like to sample). The code must operate on exactly n qubits.
      It does NOT need to include measurements; this function will add them.
  - n: int
      Number of qubits (and measured bits). Must satisfy n >= 1.

Behavior:
  1) Parses the QASM and verifies the circuit uses exactly n qubits.
  2) Builds a measurement wrapper that measures all n qubits into n classical bits.
  3) Runs the wrapped circuit on AerSimulator for 'shots' shots.
  4) Finds the bitstring with the largest count and returns it and its
     empirical probability (count/shots).

Output:
  - winner_state: str
      The most frequent n-bit measurement string (MSB-left as returned by Qiskit, e.g., '000...0' or '111...1' for GHZ).

Raises:
  - ValueError on invalid inputs or qubit-count mismatch.
  - Qiskit parsing/simulation exceptions are propagated with context.
"""

def universal_execute(qasm: str, n: int):

    shots=1024
    if not isinstance(n, int) or n < 1:
        raise ValueError("n must be a positive integer")


    try:
        dut = loads(qasm)
    except Exception as e:
        raise ValueError(f"QASM parsing failed: {e}")

    if dut.num_qubits != n:
        raise ValueError(f"Qubit count mismatch: expected {n}, got {dut.num_qubits}")


    wrapper = QuantumCircuit(n, n)
    wrapper.compose(dut, qubits=wrapper.qubits, inplace=True)
    wrapper.barrier()
    wrapper.measure(range(n), range(n))


    sim = AerSimulator()
    compiled = transpile(wrapper, sim)
    result = sim.run(compiled, shots=shots).result()
    counts = result.get_counts(compiled)


    winner_state = max(counts, key=counts.get)
    winner_prob = counts[winner_state] / shots

    return winner_state

if __name__ == "__main__":
    qasm = '''
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit[3] q;
    h q[0];
    cx q[0], q[1];
    cx q[0], q[2];
    '''
    n = 3
    success, rate, report = universal_check(qasm, n)
    print("Success:", success)
    print("Success rate:", rate)
    print("Report:", report)
