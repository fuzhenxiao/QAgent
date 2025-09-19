# tools needed for qrng algorithm
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.qasm3 import dump
from qiskit_aer import AerSimulator
from scipy.stats import chisquare, entropy
from io import StringIO

def initialize_rng_circuit(n):
    qc=QuantumCircuit(n, n)
    return qc
def apply_h_gates(qc,n):
    qc.h(range(n))
    return qc
def apply_measure_layer(qc,n):
    qc.measure(range(n), range(n))
    return qc

def circuit_to_qasm_string(circuit):
    """Convert a QuantumCircuit to QASM string."""
    buf = StringIO()
    dump(circuit, buf)
    return buf.getvalue()


if __name__ == "__main__":
    n=5
    qc=initialize_rng_circuit(n)
    qc=apply_h_gates(qc,n)
    qc=apply_measure_layer(qc,n)
    print(circuit_to_qasm_string(qc))