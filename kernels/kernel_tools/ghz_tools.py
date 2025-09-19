# tools needed for ghz algorithm
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.qasm3 import dump
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector
from io import StringIO


def initialize_ghz_circuit(n):
    circuit = QuantumCircuit(n)
    return circuit

def apply_one_h_gate(circuit):
    circuit.h(0)
    return circuit
def apply_cx_gates(circuit,n):
    for i in range(1, n):
        circuit.cx(0, i)
    return circuit


def circuit_to_qasm_string(circuit):
    """Convert a QuantumCircuit to QASM string."""
    buf = StringIO()
    dump(circuit, buf)
    return buf.getvalue()


if __name__ == "__main__":
    n=4
    c=initialize_ghz_circuit(n)
    c=apply_one_h_gate(c)
    c=apply_cx_gates(c,n)
    print(circuit_to_qasm_string(c))