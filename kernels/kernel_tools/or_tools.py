from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit.library import OrGate
from qiskit.qasm3 import loads,dump
from io import StringIO

def circuit_to_qasm_str(circuit):
    buf = StringIO()
    dump(circuit, buf)
    return buf.getvalue()

def create_input_registers(n):
    inputs=QuantumRegister(n, "in")
    return inputs

def create_output_register():
    out = QuantumRegister(1, "out")
    return out

def create_or_circuit(inputs,out,n):

    qc = QuantumCircuit(inputs, out)
    qc.append(OrGate(num_variable_qubits=n), [*inputs, out[0]])
    return qc

if __name__ == "__main__":
    n=4
    i=create_input_registers(n)
    o=create_output_register()
    qc=create_or_circuit(i,o,n)
    print(circuit_to_qasm_str(qc))

