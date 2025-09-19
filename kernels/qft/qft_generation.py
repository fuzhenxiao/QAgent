from qiskit import QuantumCircuit
from math import pi


def generate_qft_circuit(n, psi_gate):
    """Generate a QFT circuit for n qubits."""
    circuit = QuantumCircuit(n)
    circuit.append(psi_gate, range(n))
    for target_qubit in range(n - 1, -1, -1):
        for control_qubit in range(target_qubit):
            angle = pi / (2 ** (target_qubit - control_qubit))
            circuit.cp(angle, control_qubit, target_qubit)
        circuit.h(target_qubit)

    #for qubit in range(n // 2):
    #    circuit.swap(qubit, n - qubit - 1)
    return circuit
# def generate_qft_circuit(n, psi_gate):
#     qc = QuantumCircuit(n)
#     qc.append(psi_gate, range(n))

#     for target in range(n - 1, -1, -1):
#         # 先受控相位，再 Hadamard
#         for control in range(target):
#             qc.cp(pi / (2 ** (target - control)), control, target)
#         qc.h(target)

#     for q in range(n // 2):          # 末尾的位反转保持不变
#         qc.swap(q, n - q - 1)
#     return qc
