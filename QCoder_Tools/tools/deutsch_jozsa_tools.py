# tools needed for deutsch_jozsa algorithm
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



def create_deutsch_jozsa_oracle_as_gate(n, is_constant, key_string):
    oracle = QuantumCircuit(n + 1)
    if is_constant:
        if key_string[-1] == "1":
            oracle.x(n)
        else:
            oracle.id(n)
    else:
        for qubit in range(n):
            if key_string[qubit] == "1":
                oracle.x(qubit)

        for qubit in range(n):
            oracle.cx(qubit, n)

        for qubit in range(n):
            if key_string[qubit] == "1":
                oracle.x(qubit)
    oracle_gate = oracle.to_gate()
    oracle_gate.name = "Oracle"
    return oracle_gate

def create_deutsch_jozsa_oracle_as_circuit(n, is_constant, key_string):
    oracle = QuantumCircuit(n + 1)
    if is_constant:
        if key_string[-1] == "1":
            oracle.x(n)
        else:
            oracle.id(n)
    else:
        for qubit in range(n):
            if key_string[qubit] == "1":
                oracle.x(qubit)

        for qubit in range(n):
            oracle.cx(qubit, n)

        for qubit in range(n):
            if key_string[qubit] == "1":
                oracle.x(qubit)
    return oracle


def create_deutsch_jozsa_circuit(n, oracle_as_gate):
    dj_circuit = QuantumCircuit(n + 1, n)
    dj_circuit.h(range(n))
    dj_circuit.x(n)
    dj_circuit.h(n)
    dj_circuit.append(oracle_as_gate, range(n + 1))
    dj_circuit.h(range(n))
    dj_circuit.measure(range(n), range(n))
    return dj_circuit

def substract_oracle_from_deutsch_jozsa_qasm(deutsch_jozsa_qasm):
    import re
    pattern = r'gate Oracle[\s\S]*?\}'
    replacement = 'include "oracle.inc";'
    new_code = re.sub(pattern, replacement, deutsch_jozsa_qasm)
    return new_code

def run_deutsch_jozsa_circuit(circuit):
    aer_sim = AerSimulator()
    circ = transpile(circuit, aer_sim)
    result = aer_sim.run(circ, shots=1).result()
    count = result.get_counts()
    key = list(count.keys())[0]
    if "1" in key:
        prediction = "balanced"
    else:
        prediction = "constant"

    return prediction

if __name__ == "__main__":
    oracle_gate=create_deutsch_jozsa_oracle_as_gate(5,True,'00000')
    full_circuit=create_deutsch_jozsa_circuit(5,oracle_gate)
    full_circ_qasm=circuit_to_qasm_str(full_circuit)
    without_oracle=substract_oracle_from_deutsch_jozsa_qasm(full_circ_qasm)
    print(without_oracle)
    print(run_deutsch_jozsa_circuit(full_circuit))