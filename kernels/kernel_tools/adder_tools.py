# tools needed for bernstein_vazirani algorithm
import random
import re
import math
from qiskit import QuantumCircuit, transpile,QuantumRegister
from qiskit.circuit.library import FullAdderGate
from qiskit.qasm3 import loads,dump
from qiskit_aer import AerSimulator
from io import StringIO

def circuit_to_qasm_str(circuit):
    buf = StringIO()
    dump(circuit, buf)
    return buf.getvalue()

def create_input_registers(n):
    a = QuantumRegister(n, "a")
    b = QuantumRegister(n, "b")
    cin = QuantumRegister(1, "cin")
    return a,b,cin

def create_carryout_register():
    cout = QuantumRegister(1, "cout")
    return cout


def create_adder_circuit(n,a,b,cin,cout):
    qc = QuantumCircuit(a, b, cin, cout)
    qc.append(FullAdderGate(n), [*a, *b, cin[0], cout[0]])
    return qc

if __name__ == "__main__":
    n=4
    a,b,cin=create_input_registers(n)
    cout=create_carryout_register()
    qc=create_adder_circuit(n,a,b,cin,cout)
    print(circuit_to_qasm_str(qc))

