from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit.library import PermutationGate
from qiskit.qasm3 import loads,dump
from io import StringIO

def circuit_to_qasm_str(circuit):
    buf = StringIO()
    dump(circuit, buf)
    return buf.getvalue()


def make_shift_permutation_pattern(n):
    pattern=[(i + 1) % n for i in range(n)]

    return pattern


def create_permutation_template_circuit(n):
    q = QuantumRegister(n, "q")
    qc = QuantumCircuit(q)
    return qc,q

def implement_permutation_logic(qc,q,pattern):
    qc.append(PermutationGate(pattern), q[:])
    return qc


if __name__ == "__main__":
    pattern=make_shift_permutation_pattern(4)

    qc,q=create_permutation_template_circuit(4)
    raw_cirq=implement_permutation_logic(qc,q,pattern)
    
    print(circuit_to_qasm_str(raw_cirq))

