
from qiskit import QuantumCircuit,QuantumRegister
from qiskit.qasm3 import loads,dump
from io import StringIO

def circuit_to_qasm_str(circuit):
    buf = StringIO()
    dump(circuit, buf)
    return buf.getvalue()

def initilize_circuit(n):
    q = QuantumRegister(n, "q")
    qc = QuantumCircuit(q)
    return qc,q

def apply_h_gates(qc,q,n):
    for i in range(n):
        qc.h(q[i])
    return qc

def apply_cz_gates(qc,q,n):
    for i in range(n - 1):
        qc.cz(q[i], q[i + 1])
    return qc

if __name__ == "__main__":
    n=4
    qc,q=initilize_circuit(n)
    qc=apply_h_gates(qc,q,n)
    qc=apply_cz_gates(qc,q,n)
    print(circuit_to_qasm_str(qc))

