# tools needed for simon algorithm
import random
import re
from io import StringIO
import numpy as np
from sympy import Matrix
from qiskit import QuantumCircuit, transpile
from qiskit.qasm3 import dump, loads
from qiskit_aer import AerSimulator
import traceback


def circuit_to_qasm_str(circuit):
    buf = StringIO()
    dump(circuit, buf)
    return buf.getvalue()


def create_simon_oracle_as_gate(n, secret_string, key_string):
    oracle = QuantumCircuit(2 * n)
    secret_string = secret_string[::-1]
    key_string = key_string[::-1]
    for qubit in range(n):
        oracle.cx(qubit, qubit + n)
    if secret_string != "0" * n:
        i = secret_string.find("1")
        for qubit in range(n):
            if secret_string[qubit] == "1":
                oracle.cx(i, qubit + n)
    for qubit in range(n, 2 * n):
        if key_string[qubit - n] == "1":
            oracle.x(qubit)
    oracle_gate = oracle.to_gate()
    oracle_gate.name = "Oracle"
    return oracle_gate


def create_simon_oracle_as_circuit(n, secret_string, key_string):
    oracle = QuantumCircuit(2 * n)
    secret_string = secret_string[::-1]
    key_string = key_string[::-1]
    for qubit in range(n):
        oracle.cx(qubit, qubit + n)
    if secret_string != "0" * n:
        i = secret_string.find("1")
        for qubit in range(n):
            if secret_string[qubit] == "1":
                oracle.cx(i, qubit + n)
    for qubit in range(n, 2 * n):
        if key_string[qubit - n] == "1":
            oracle.x(qubit)

    return oracle



def create_simon_circuit(n, oracle_as_gate):

    simon_circuit = QuantumCircuit(2 * n, n)
    simon_circuit.h(range(n))
    simon_circuit.append(oracle_as_gate, range(2 * n))
    simon_circuit.h(range(n))
    simon_circuit.measure(range(n), range(n))

    return simon_circuit

def substract_oracle_from_simon_qasm(simon_qasm):
    import re
    pattern = r'gate Oracle[\s\S]*?\}'
    replacement = 'include "oracle.inc";'

    new_code = re.sub(pattern, replacement, simon_qasm)
    return new_code








# -------------------------------------------------------------------
def generate_random_strings_specially_for_simon(n, test_num=5):

    result = []
    for _ in range(test_num):
        if random.choice([True, False]):
            s_str = "0" * n
        else:
            # For nontrivial, ensure at least two '1's.
            m = random.randint(2, n)
            ones_positions = random.sample(range(n), m)
            s = ['0'] * n
            for pos in ones_positions:
                s[pos] = '1'
            s_str = ''.join(s)
        result.append(s_str)
    return result




def run_simon_circuit(simon_circuit, n,shots=100):
    def binary_rank_and_nullspace(equations, n):
        M = [eq[:] for eq in equations]  # copy
        m = len(M)
        pivot_cols = []
        row_idx = 0
        for col in range(n):
            pivot = None
            for r in range(row_idx, m):
                if M[r][col] == 1:
                    pivot = r
                    break
            if pivot is None:
                continue
            # Swap the found row with the current pivot row.
            M[row_idx], M[pivot] = M[pivot], M[row_idx]
            pivot_cols.append(col)
            # Eliminate 1's in this column from all other rows.
            for r in range(m):
                if r != row_idx and M[r][col] == 1:
                    for c in range(col, n):
                        M[r][c] = (M[r][c] + M[row_idx][c]) % 2
            row_idx += 1
            if row_idx == m:
                break
        rank = len(pivot_cols)

        candidate = None
        for candidate_bits in range(1, 1 << n):
            candidate_vec = [(candidate_bits >> i) & 1 for i in range(n)]
            valid = True
            for eq in equations:
                if sum(e * c for e, c in zip(eq, candidate_vec)) % 2 != 0:
                    valid = False
                    break
            if valid:
                candidate = candidate_vec
                break
        if candidate is None:
            candidate = [0] * n
        return rank, candidate

    aer_sim = AerSimulator()
    min_independent_eq = n - 1
    equations = []
    iteration = 0
    circuit=simon_circuit
    while iteration < 10:
        circ = transpile(circuit, basis_gates=['u3','cx'])
        results = aer_sim.run(circ, shots=shots).result()
        counts = results.get_counts()
        for result, count in counts.items():
            if result != "0" * n:
                # Convert the bitstring (as given by Qiskit) to a list of integers.
                eq = [int(bit) for bit in result]
                equations.append(eq)
        # Check if we have collected enough (linearly independent) equations.
        if len(equations) >= min_independent_eq:
            rank, candidate = binary_rank_and_nullspace(equations, n)
            if rank >= min_independent_eq:
                candidate_str = "".join(str(bit) for bit in candidate)
                return candidate_str
        iteration += 1
    # If the loop ends without reaching enough independent equations,
    # try to return the best candidate computed from the accumulated outcomes.
    if equations:
        _, candidate = binary_rank_and_nullspace(equations, n)
        candidate_str = "".join(str(bit) for bit in candidate)
        return candidate_str
    else:
        return "0" * n


if __name__ == "__main__":

    oracle_gate=create_simon_oracle_as_gate(5,'00101','00100')
    full_circuit=create_simon_circuit(5,oracle_gate)
    full_circ_qasm=circuit_to_qasm_str(full_circuit)
    without_oracle=substract_oracle_from_simon_qasm(full_circ_qasm)
    print(without_oracle)
    print(run_simon_circuit(full_circuit,5))