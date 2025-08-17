# tools needed for grover algorithm
import math
from io import StringIO
from qiskit import QuantumCircuit, transpile
from qiskit.qasm3 import dump, loads
from qiskit_aer import AerSimulator
import random
import re

def circuit_to_qasm_str(circuit):
    buf = StringIO()
    dump(circuit, buf)
    return buf.getvalue()

def create_grover_oracle_as_gate(n, marked_state):
    oracle = QuantumCircuit(n)
    rev_target = marked_state[::-1]
    zero_inds = [i for i, c in enumerate(rev_target) if c == "0"]
    if zero_inds:
        oracle.x(zero_inds)
    oracle.h(n - 1)
    oracle.mcx(list(range(n - 1)), n - 1)
    oracle.h(n - 1)
    if zero_inds:
        oracle.x(zero_inds)
    oracle_gate = oracle.to_gate()
    oracle_gate.name = "Oracle"
    return oracle_gate

def create_grover_oracle_as_circuit(n, marked_state):
    oracle = QuantumCircuit(n)
    rev_target = marked_state[::-1]
    zero_inds = [i for i, c in enumerate(rev_target) if c == "0"]
    if zero_inds:
        oracle.x(zero_inds)
    oracle.h(n - 1)
    oracle.mcx(list(range(n - 1)), n - 1)
    oracle.h(n - 1)
    if zero_inds:
        oracle.x(zero_inds)
    return oracle

def create_grover_circuit(n, oracle_as_gate):
    #create full grover circuit based on provided oracle gate, return a circuit
    def diffusion_operator(n):
        """Create the diffusion operator for n qubits."""
        diffuser = QuantumCircuit(n)
        diffuser.h(range(n))
        diffuser.x(range(n))

        diffuser.h(n - 1)
        diffuser.mcx(list(range(n - 1)), n - 1)
        diffuser.h(n - 1)

        diffuser.x(range(n))
        diffuser.h(range(n))

        diffuser_gate = diffuser.to_gate()
        diffuser_gate.name = "Diffuser"
        return diffuser_gate
    num_iterations = math.floor(math.pi / 4 * math.sqrt(2**n))
    circuit = QuantumCircuit(n, n)
    circuit.h(range(n))

    diffuser = diffusion_operator(n)

    # Apply the oracle and the diffuser for the optimal number of iterations
    for _ in range(num_iterations):
        circuit.append(oracle_as_gate, range(n))
        circuit.append(diffuser, range(n))

    circuit.measure(range(n), range(n))
    return circuit


# def substract_oracle_from_grover_qasm(grover_qasm):
#     import re
#     pattern = r'gate Oracle[\s\S]*?\}'
#     replacement = 'include "oracle.inc";'

#     new_code = re.sub(pattern, replacement, grover_qasm)
#     return new_code

def substract_oracle_from_grover_qasm(qasm_str):
    import re

    lines = qasm_str.strip().splitlines()

    # Step 1: Remove all gate definitions except 'Diffuser'
    cleaned_lines = []
    in_gate = False
    gate_name = ""
    gate_buffer = []

    for line in lines:
        stripped = line.strip()
        # Start of gate
        if stripped.startswith("gate "):
            in_gate = True
            gate_buffer = [line]
            gate_name = stripped.split()[1].split('(')[0]  # Remove parameter if present
            continue
        if in_gate:
            gate_buffer.append(line)
            if "}" in stripped:
                in_gate = False
                if gate_name == "Diffuser":
                    cleaned_lines.extend(gate_buffer)
                # else discard gate_buffer
            continue
        else:
            cleaned_lines.append(line)

    # Step 2: Insert oracle.inc after stdgates.inc
    result = []
    inserted_oracle = False
    for line in cleaned_lines:
        result.append(line)
        if line.strip() == 'include "stdgates.inc";' and not inserted_oracle:
            result.append('include "oracle.inc";')
            inserted_oracle = True

    # Step 3: Clean empty lines
    cleaned_result = '\n'.join(result)
    cleaned_result = re.sub(r'\n\s*\n+', '\n', cleaned_result).strip()

    return cleaned_result


    
def run_grover_circuit(grover_circuit, shots=100):
    aer_sim = AerSimulator()
    transpiled = transpile(grover_circuit, aer_sim)
    result = aer_sim.run(transpiled, shots=shots).result()
    counts = result.get_counts()
    predicted = max(counts, key=counts.get)
    return predicted



# 主程序
if __name__ == "__main__":
    oracle_gate=create_grover_oracle_as_gate(5,'00101')
    full_circuit=create_grover_circuit(5,oracle_gate)
    full_circ_qasm=circuit_to_qasm_str(full_circuit)
    #print(full_circ_qasm)
    without_oracle=substract_oracle_from_grover_qasm(full_circ_qasm)
    print(without_oracle)
    print(run_grover_circuit(full_circuit))

