# tools needed for w_state algorithm
import numpy as np
import math
from qiskit import QuantumCircuit, transpile
from qiskit.qasm3 import dump
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector, DensityMatrix, partial_trace
from io import StringIO



def initialize_w_state_circuit(n):
    qc = QuantumCircuit(n, n)
    return qc

def apply_one_x_gate(qc,n):
    qc.x(n-1)
    return qc

def apply_F_gate(qc,n):

    def F_circuit(circuit, i, j, n, k):
        theta = math.acos(math.sqrt(1.0 / (n - k + 1)))
        circuit.ry(-theta, j)
        circuit.cz(i, j)
        circuit.ry(theta, j)

    for i in range(0, n - 1):
        F_circuit(qc, n - 1 - i, n - 2 - i, n, i + 1)
    return qc

def apply_cx_gates(qc,n):

    for i in range(0, n - 1):
        qc.cx(n - 2 - i, n - 1 - i)
    return qc


def circuit_to_qasm_string(circuit):
    """Convert a QuantumCircuit to QASM string."""
    buf = StringIO()
    dump(circuit, buf)
    return buf.getvalue()


if __name__ == "__main__":
    n=4
    qc=initialize_w_state_circuit(n)
    qc=apply_one_x_gate(qc,n)
    qc=apply_F_gate(qc,n)
    qc=apply_cx_gates(qc,n)
    print(circuit_to_qasm_string(qc))

