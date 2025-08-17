# tools needed for simon_multi algorithm
import random
import re
from io import StringIO
import numpy as np
from sympy import Matrix
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit.qasm3 import dump, loads
from qiskit_aer import AerSimulator


def circuit_to_qasm_str(circuit):
    buf = StringIO()
    dump(circuit, buf)
    return buf.getvalue()


def create_multi_simon_oracle_as_gate(n, s1, s2, key_string):
    qr = QuantumRegister(2 * n)
    ancilla = QuantumRegister(1)
    multi_simon_oracle = QuantumCircuit(qr, ancilla)

    s1 = s1[::-1]
    s2 = s2[::-1]
    key_string = key_string[::-1]

    oracle1 = QuantumCircuit(qr)
    for qubit in range(n):
        oracle1.cx(qubit, qubit + n)
    if s1 != "0" * n:
        i = s1.find("1")
        for qubit in range(n):
            if s1[qubit] == "1":
                oracle1.cx(i, qubit + n)
    oracle1_gate = oracle1.to_gate()
    multi_simon_oracle.append(oracle1_gate.control(1), [ancilla[0]] + qr[:])
    multi_simon_oracle.x(ancilla[0])

    oracle2 = QuantumCircuit(qr)
    for qubit in range(n):
        oracle2.cx(qubit, qubit + n)
    if s2 != "0" * n:
        i = s2.find("1")
        for qubit in range(n):
            if s2[qubit] == "1":
                oracle2.cx(i, qubit + n)
    oracle2_gate = oracle2.to_gate()
    multi_simon_oracle.append(oracle2_gate.control(1), [ancilla[0]] + qr[:])

    for qubit in range(n, 2 * n):
        if key_string[qubit - n] == "1":
            multi_simon_oracle.x(qr[qubit])

    oracle_gate = multi_simon_oracle.to_gate()
    oracle_gate.name = "Oracle"
    return oracle_gate


def create_multi_simon_oracle_as_circuit(n, s1, s2, key_string):
    qr = QuantumRegister(2 * n)
    ancilla = QuantumRegister(1)
    multi_simon_oracle = QuantumCircuit(qr, ancilla)

    s1 = s1[::-1]
    s2 = s2[::-1]
    key_string = key_string[::-1]

    oracle1 = QuantumCircuit(qr)
    for qubit in range(n):
        oracle1.cx(qubit, qubit + n)
    if s1 != "0" * n:
        i = s1.find("1")
        for qubit in range(n):
            if s1[qubit] == "1":
                oracle1.cx(i, qubit + n)
    multi_simon_oracle.append(oracle1, qr)

    multi_simon_oracle.x(ancilla[0])

    oracle2 = QuantumCircuit(qr)
    for qubit in range(n):
        oracle2.cx(qubit, qubit + n)
    if s2 != "0" * n:
        i = s2.find("1")
        for qubit in range(n):
            if s2[qubit] == "1":
                oracle2.cx(i, qubit + n)
    multi_simon_oracle.append(oracle2, qr)

    for qubit in range(n, 2 * n):
        if key_string[qubit - n] == "1":
            multi_simon_oracle.x(qr[qubit])

    return multi_simon_oracle


def create_multi_simon_circuit(n, oracle_gate):
    qr = QuantumRegister(2 * n + 1,name='q')
    cr = ClassicalRegister(n + 1,name='c')
    circuit = QuantumCircuit(qr, cr)

    circuit.h(range(n))
    circuit.h(2 * n)

    circuit.append(oracle_gate, qr)
    circuit.h(range(n))
    circuit.measure(range(n), range(n))
    circuit.measure(2 * n, n)
    return circuit
    
def generate_random_string_specially_for_multi_simon(n):
    ones_count = random.choice([0, 1, 2])
    positions = random.sample(range(n), ones_count)
    s = ['0'] * n
    for pos in positions:
        s[pos] = '1'
    return ''.join(s)

def substract_oracle_from_multi_simon_qasm(qasm_str):
    pattern0 = r'gate _ccircuit[\s\S]*?\}'
    qasm_str=re.sub(pattern0, '', qasm_str)
    pattern = r'gate Oracle[\s\S]*?\}'
    replacement = 'include "oracle.inc";'
    new_qasm = re.sub(pattern, replacement, qasm_str)
    new_qasm = qasm_str = re.sub(r'\n\s*\n+', '\n', new_qasm).strip()
    return new_qasm


def run_multi_simon_circuit(circuit, n, shots=100):
    def mod2(x):
        return x.as_numer_denom()[0] % 2

    def post_process(equations):
        M = Matrix(equations).T
        M_I = Matrix(np.hstack([M, np.eye(M.shape[0], dtype=int)]))
        M_I_rref = M_I.rref(iszerofunc=lambda x: x % 2 == 0)
        M_I_final = M_I_rref[0].applyfunc(mod2)
        if all(value == 0 for value in M_I_final[-1, :M.shape[1]]):
            result_s = "".join(str(c) for c in M_I_final[-1, M.shape[1]:])
        else:
            result_s = '0' * M.shape[0]
        return result_s

    aer_sim = AerSimulator()
    transpiled = transpile(circuit, aer_sim)
    results = aer_sim.run(transpiled, shots=shots).result()
    counts = results.get_counts()

    dic1, dic2 = {}, {}
    for bitstring, count in counts.items():
        if bitstring[0] == '1':
            dic1[bitstring[1:]] = count
        else:
            dic2[bitstring[1:]] = count

    def recover(dic):
        equations = []
        for result, count in dic.items():
            if result != '0' * n:
                y = [int(bit) for bit in result]
                equations.append(y)
        if len(equations) == 0:
            return '0' * n
        else:
            return post_process(equations)

    pred1 = recover(dic2)
    pred2 = recover(dic1)

    return pred1, pred2


if __name__ == "__main__":
    oracle_gate = create_multi_simon_oracle_as_gate(7, '0110000', '0010010', '0001000')
    full_circuit = create_multi_simon_circuit(7, oracle_gate)
    full_circ_qasm = circuit_to_qasm_str(full_circuit)
    without_oracle = substract_oracle_from_multi_simon_qasm(full_circ_qasm)
    print(without_oracle)
    print(run_multi_simon_circuit(full_circuit, 7))





