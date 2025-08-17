# tools needed for bernstein_vazirani algorithm
import random
import re
import math
from qiskit import QuantumCircuit, transpile
from qiskit.qasm3 import loads,dump
from qiskit_aer import AerSimulator
from io import StringIO
def circuit_to_qasm_str(circuit):
    buf = StringIO()
    dump(circuit, buf)
    return buf.getvalue()

def create_bernstein_vazirani_oracle_as_gate(n, secret_string):
    """Generates the oracle for the Bernstein-Vazirani algorithm."""
    oracle = QuantumCircuit(n + 1)
    s = secret_string[::-1]
    for qubit in range(n):
        if s[qubit] == "1":
            oracle.cx(qubit, n)
    oracle_gate = oracle.to_gate()
    oracle_gate.name = "Oracle"

    return oracle_gate

def create_bernstein_vazirani_oracle_as_circuit(n, secret_string):
    """Generates the oracle for the Bernstein-Vazirani algorithm."""
    oracle = QuantumCircuit(n + 1)
    s = secret_string[::-1]
    for qubit in range(n):
        if s[qubit] == "1":
            oracle.cx(qubit, n)
    return oracle

def create_bernstein_vazirani_circuit(n, oracle_as_gate):

    bv_circuit = QuantumCircuit(n + 1, n)
    bv_circuit.h(range(n))
    bv_circuit.x(n)
    bv_circuit.h(n)
    bv_circuit.append(oracle_as_gate, range(n + 1))
    bv_circuit.h(range(n))
    bv_circuit.measure(range(n), range(n))
    return bv_circuit

def substract_oracle_from_bernstein_vazirani_qasm(bernstein_vazirani_qasm):
    import re
    pattern = r'gate Oracle[\s\S]*?\}'
    replacement = 'include "oracle.inc";'
    new_code = re.sub(pattern, replacement, bernstein_vazirani_qasm)
    return new_code

def run_bernstein_vazirani_circuit(circuit):
    aer_sim = AerSimulator()
    circ = transpile(circuit, aer_sim)
    result = aer_sim.run(circ, shots=500).result()
    counts = result.get_counts()
    return list(counts.keys())[0]


if __name__ == "__main__":

    oracle_gate=create_bernstein_vazirani_oracle_as_gate(5,'00101')
    full_circuit=create_bernstein_vazirani_circuit(5,oracle_gate)
    full_circ_qasm=circuit_to_qasm_str(full_circuit)
    without_oracle=substract_oracle_from_bernstein_vazirani_qasm(full_circ_qasm)
    print(without_oracle)
    print(run_bernstein_vazirani_circuit(full_circuit))