# tools needed for qft algorithm
from qiskit.qasm3 import dump
from io import StringIO
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import QFT
from qiskit_aer import AerSimulator
import numpy as np


def initialize_qft_circuit(n):
    qc=QuantumCircuit(n,n)
    return qc

def apply_qft_gate(qc,n):
    qc.append(QFT(num_qubits=n, do_swaps=False), range(n))
    return qc

def apply_measure_layer(qc,n):
    qc.measure(range(n), range(n))
    return qc


def circuit_to_qasm_str(circuit):
    buf = StringIO()
    decomposed = circuit
    while True:
        new_circuit = decomposed.decompose()
        if new_circuit == decomposed:
            break
        decomposed = new_circuit
    dump(decomposed, buf)
    return buf.getvalue()


if __name__ == "__main__":
    n=4
    qc=initialize_qft_circuit(n)
    qc=apply_qft_gate(qc,n)
    qc=apply_measure_layer(qc,n)
    print(circuit_to_qasm_str(qc))

