from qiskit import QuantumCircuit,QuantumRegister
from qiskit.qasm3 import dump,dumps
from qiskit.circuit.library import FullAdderGate
import sys

# def make_nbit_adder_qasm(n: int) -> str:

#     qc = QuantumCircuit(2*n+2)
#     qc.append(FullAdderGate(n))
#     return qc

# if __name__ == "__main__":
#     n = int(3)
#     print(make_nbit_adder_qasm(n).dumps())

def make_nbit_adder_qc(n: int) -> QuantumCircuit:
    if not (2 <= n <= 14):
        raise ValueError("n must be between 2 and 14")
    # Registers: a[n], b[n], plus single-bit cin and cout
    a = QuantumRegister(n, "a")
    b = QuantumRegister(n, "b")
    cin = QuantumRegister(1, "cin")
    cout = QuantumRegister(1, "cout")
    qc = QuantumCircuit(a, b, cin, cout)

    # Optional: set carry-in = 1
    # qc.x(cin[0])

    # Append the generic full-adder gate: qargs order is [a..., b..., cin, cout]
    qc.append(FullAdderGate(n), [*a, *b, cin[0], cout[0]])
    return qc

# --- QASM 3 (if you prefer) ---
def make_nbit_adder_qasm3(n: int) -> str:
    # Requires: from qiskit.qasm3 import dumps
    from qiskit.qasm3 import dumps
    return dumps(make_nbit_adder_qc(n))

def save_nbit_adder_qasm3(n):
    from qiskit.qasm3 import dump
    with open(f"./adder_n{n}.qasm", "w") as file:
        dump(make_nbit_adder_qc(n), file)

if __name__ == "__main__":
    for i in range(2,14):    
        n = i
        qc = make_nbit_adder_qc(n)
        print(qc)                 # ascii circuit
        save_nbit_adder_qasm3(n)  # or print(make_nbit_adder_qasm3(n))
