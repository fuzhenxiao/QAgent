
import sys
from qiskit import QuantumCircuit, QuantumRegister
from qiskit.qasm3 import dump, dumps


def make_cluster_qc(n: int) -> QuantumCircuit:
    if n < 1:
        raise ValueError("Number of qubits n must be >= 1")
    q = QuantumRegister(n, "q")
    qc = QuantumCircuit(q)

    # Step 1: |+>^n
    for i in range(n):
        qc.h(q[i])

    # Step 2: CZ between neighbors (linear chain)
    for i in range(n - 1):
        qc.cz(q[i], q[i + 1])

    return qc


def make_cluster_qasm3(n: int) -> str:
    return dumps(make_cluster_qc(n))


def save_cluster_qasm3(n: int):
    with open(f"./cluster_n{n}.qasm", "w") as f:
        dump(make_cluster_qc(n), f)


if __name__ == "__main__":
    for n in range(2,14):
        qc = make_cluster_qc(n)
        print(f"\nCluster state for n={n}")
        print(qc)
        save_cluster_qasm3(n)
