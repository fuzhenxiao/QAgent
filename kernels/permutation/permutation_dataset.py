from qiskit import QuantumCircuit, QuantumRegister
from qiskit.qasm3 import dump, dumps
from qiskit.circuit.library import PermutationGate
import sys


def make_shift_permutation_pattern(n: int) -> list[int]:
    """
    Generate a one-position cyclic permutation pattern for n qubits.
    Example: n=4 -> [1, 2, 3, 0]
    """
    return [(i + 1) % n for i in range(n)]


def make_permutation_qc(n: int) -> QuantumCircuit:
    """
    Create a circuit with a PermutationGate applying a one-position shift.
    """
    if n < 2:
        raise ValueError("Number of qubits must be >= 2")

    pattern = make_shift_permutation_pattern(n)
    q = QuantumRegister(n, "q")
    qc = QuantumCircuit(q)

    qc.append(PermutationGate(pattern), q[:])
    return qc


def make_permutation_qasm3(n: int) -> str:
    return dumps(make_permutation_qc(n))


def save_permutation_qasm3(n: int):
    with open(f"./permulation_n{n}.qasm", "w") as file:
        dump(make_permutation_qc(n), file)


if __name__ == "__main__":

    for n in range(2, 14):
        qc = make_permutation_qc(n)
        print(f"Permutation pattern for {n} qubits: {make_shift_permutation_pattern(n)}")
        print(qc)
        save_permutation_qasm3(n)
