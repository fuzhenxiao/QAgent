from qiskit import QuantumCircuit, QuantumRegister
from qiskit.qasm3 import dump, dumps
from qiskit.circuit.library import OrGate


def make_nbit_or_qc(n: int) -> QuantumCircuit:
    if not (2 <= n <= 14):
        raise ValueError("n must be between 2 and 14")

    # Input register (n qubits) + output register (1 qubit)
    inputs = QuantumRegister(n, "in")
    out = QuantumRegister(1, "out")
    qc = QuantumCircuit(inputs, out)

    # Append the OrGate: expects [*inputs, out]
    qc.append(OrGate(num_variable_qubits=n), [*inputs, out[0]])
    return qc


def make_nbit_or_qasm3(n: int) -> str:
    return dumps(make_nbit_or_qc(n))


def save_nbit_or_qasm3(n: int):
    with open(f"./or_n{n}.qasm", "w") as file:
        dump(make_nbit_or_qc(n), file)


if __name__ == "__main__":
    for i in range(2, 14):
        n = i
        qc = make_nbit_or_qc(n)
        print(qc)                 # ASCII circuit diagram
        save_nbit_or_qasm3(n)     # Saves to `or_n{n}.qasm`
