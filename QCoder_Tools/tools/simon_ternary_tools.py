# tools needed for simon_ternary algorithm
import numpy as np
from sympy import Matrix, S
from qiskit import QuantumCircuit, QuantumRegister, transpile
from qiskit.quantum_info import Operator
from qiskit.qasm3 import dump
from qiskit_aer import AerSimulator
import re
from io import StringIO
import math
from qiskit.circuit.library import XGate
def circuit_to_qasm_str(circuit):
    def replace_igh_and_rcccx_dg(qasm_string):
        lines = qasm_string.splitlines()
        new_lines = []
        inside_igh_definition = False
        inside_rcccx_dg_definition = False

        for line in lines:
            if "gate IGH" in line:
                inside_igh_definition = True
                continue
            if inside_igh_definition and "}" in line:
                inside_igh_definition = False
                continue

            if "gate rcccx_dg" in line:
                inside_rcccx_dg_definition = True
                continue
            if inside_rcccx_dg_definition and "}" in line:
                inside_rcccx_dg_definition = False
                continue

            if not inside_igh_definition and not inside_rcccx_dg_definition:
                new_line = line.replace("IGH", "inv @ GH")
                new_line = new_line.replace("rcccx_dg", "inv @ rcccx")
                new_lines.append(new_line)

        optimized_qasm = "\n".join(new_lines)
        return optimized_qasm


    def detect_and_replace_duplicate_gates(qasm_string):
        gate_definitions = {}
        gate_replacement_mapping = {}
        gate_counter = 1

        gate_pattern = re.compile(r'gate\s+(\w+)\s*\(([^)]*)\)\s+(\w+(?:,\s*\w+)*)\s*\{([^}]*)\}', re.DOTALL)
        matches = gate_pattern.findall(qasm_string)

        for match in matches:
            gate_name, gate_params, gate_qubits, gate_body = match
            gate_body = gate_body.strip()
            gate_signature = (gate_params.strip(), gate_qubits.strip(), gate_body)
            if gate_signature in gate_definitions:
                gate_replacement_mapping[gate_name] = gate_definitions[gate_signature]
            else:
                new_name = f"cu_{gate_counter}"
                gate_definitions[gate_signature] = new_name
                gate_replacement_mapping[gate_name] = new_name
                gate_counter += 1


        optimized_qasm = qasm_string
        for old_name, new_name in gate_replacement_mapping.items():
            optimized_qasm = optimized_qasm.replace(old_name, new_name)

        qasm_string = optimized_qasm
        gate_pattern = re.compile(r'gate\s+(\w+)\s*\(([^)]*)\)\s+(\w+(?:,\s*\w+)*)\s*\{([^}]*)\}', re.DOTALL)
        matches = gate_pattern.findall(qasm_string)

        header_pattern = re.compile(r'OPENQASM\s+3;\s*include\s+\"stdgates\.inc\";\s*', re.DOTALL)
        header_match = header_pattern.search(qasm_string)
        if header_match:
            header = header_match.group(0)
        else:
            header = "OPENQASM 3;\ninclude \"stdgates.inc\";\n"

        unique_gate_definitions = set()
        gate_definitions_section = []

        for match in matches:
            gate_name, gate_params, gate_qubits, gate_body = match
            gate_body = gate_body.strip()
            gate_signature = (gate_params.strip(), gate_qubits.strip(), gate_body)
            if gate_signature not in unique_gate_definitions:
                unique_gate_definitions.add(gate_signature)
                gate_definitions_section.append(
                    f"gate {gate_name} ({gate_params}) {gate_qubits} {{{gate_body}}}")

        non_gate_qasm = gate_pattern.sub('', optimized_qasm).strip()
        non_gate_qasm = header_pattern.sub('', non_gate_qasm).strip()

        optimized_qasm = '\n\n'.join([header] + gate_definitions_section + [non_gate_qasm])

        return optimized_qasm


    def detect_and_remove_redundant_gates(qasm_string):
        redundant_gates = set()
        gate_pattern = re.compile(r'gate\s+(\w+)\s+([^{]+)\s*\{\s*mcx\s+([^{]+)\s*;\s*\}', re.DOTALL)
        matches = gate_pattern.findall(qasm_string)

        for match in matches:
            gate_name, gate_params, mcx_params = match
            if gate_params.strip() == mcx_params.strip():
                redundant_gates.add(gate_name)

        optimized_qasm = qasm_string
        for gate_name in redundant_gates:
            optimized_qasm = re.sub(rf'gate\s+{gate_name}\s+[^{{]+\{{[^}}]*\}}', '', optimized_qasm)

        for gate_name in redundant_gates:
            optimized_qasm = re.sub(rf'\b{gate_name}\b', 'mcx', optimized_qasm)

        optimized_qasm = re.sub(r'\n\s*\n', '\n', optimized_qasm).strip()

        return optimized_qasm
    buf = StringIO()
    dump(circuit, buf)
    txt=buf.getvalue()
    optimized_qasm = replace_igh_and_rcccx_dg(txt)
    optimized_qasm = detect_and_replace_duplicate_gates(optimized_qasm)
    optimized_qasm = detect_and_remove_redundant_gates(optimized_qasm)

    return optimized_qasm

def create_simon_ternary_oracle_as_gate(n, secret_string, key_string):
    """Creates a Ternary Simon oracle for the given secret string s"""

    def find_ternary_cycles(n, secret_string):

        def generate_ternary_numbers(qudits_num):

            if qudits_num == 0:
                return [""]
            smaller = generate_ternary_numbers(qudits_num - 1)
            return [x + y for x in smaller for y in "012"]

        def add_ternary(t1, t2):

            return ''.join(str((int(t1[i]) + int(t2[i])) % 3) for i in range(len(t1)))

        def find_cycle(start, secret_string):

            current = start
            ternary_cycle = []
            seen_cycles = set()
            while current not in seen_cycles:
                seen_cycles.add(current)
                ternary_cycle.append(current)
                current = add_ternary(current, secret_string)
            return ternary_cycle

        # Generate all n-digit ternary numbers
        ternary_numbers = generate_ternary_numbers(n)

        # Initialize the list of cycles and a set to track seen numbers
        cycles = []
        seen = set()

        # Iterate over all ternary numbers and find the cycle for each unseen number
        for number in ternary_numbers:
            if number not in seen:
                cycle = find_cycle(number, secret_string)
                cycles.append(cycle)
                seen.update(cycle)

        return cycles

    cycles = find_ternary_cycles(n, secret_string)

    # Define the quantum registers: 2n for the Simon problem, fewer qubits for the compressed encoding
    qr1 = QuantumRegister(2 * n)
    qr2 = QuantumRegister(math.ceil(math.log2(len(cycles))))
    oracle = QuantumCircuit(qr1, qr2)

    base_gate = XGate()

    for cycle_idx, cycle in enumerate(cycles):
        binary_idx = format(cycle_idx, f'0{math.ceil(math.log2(len(cycles)))}b')  # Binary encoding of the cycle index
        for number in cycle:
            ctrl_states = ''.join(format(int(digit), '02b') for digit in number)
            # For each bit in the binary index, add control logic to the corresponding ancilla qubit
            for bit_pos, bit in enumerate(binary_idx):
                if bit == '1':
                    cgate = base_gate.control(num_ctrl_qubits=len(ctrl_states), ctrl_state=ctrl_states)
                    oracle.append(cgate, qr1[:len(ctrl_states)] + [qr2[bit_pos]])

    for qubit in range(2 * n, math.ceil(math.log2(len(cycles)))):
        key_string2 = ''.join(format(int(digit), '02b') for digit in key_string)
        if key_string2[qubit - n] == "1":
            oracle.x(qubit)

    oracle_gate = oracle.to_gate()
    oracle_gate.name = "Oracle"

    return oracle_gate

def create_simon_ternary_oracle_as_circuit(n, secret_string, key_string):
    """Creates a Ternary Simon oracle for the given secret string s"""
    def find_ternary_cycles(n, secret_string):

        def generate_ternary_numbers(qudits_num):

            if qudits_num == 0:
                return [""]
            smaller = generate_ternary_numbers(qudits_num - 1)
            return [x + y for x in smaller for y in "012"]

        def add_ternary(t1, t2):

            return ''.join(str((int(t1[i]) + int(t2[i])) % 3) for i in range(len(t1)))

        def find_cycle(start, secret_string):

            current = start
            ternary_cycle = []
            seen_cycles = set()
            while current not in seen_cycles:
                seen_cycles.add(current)
                ternary_cycle.append(current)
                current = add_ternary(current, secret_string)
            return ternary_cycle

        # Generate all n-digit ternary numbers
        ternary_numbers = generate_ternary_numbers(n)

        # Initialize the list of cycles and a set to track seen numbers
        cycles = []
        seen = set()

        # Iterate over all ternary numbers and find the cycle for each unseen number
        for number in ternary_numbers:
            if number not in seen:
                cycle = find_cycle(number, secret_string)
                cycles.append(cycle)
                seen.update(cycle)

        return cycles

    cycles = find_ternary_cycles(n, secret_string)

    # Define the quantum registers: 2n for the Simon problem, fewer qubits for the compressed encoding
    qr1 = QuantumRegister(2 * n)
    qr2 = QuantumRegister(math.ceil(math.log2(len(cycles))))
    oracle = QuantumCircuit(qr1, qr2)

    base_gate = XGate()

    for cycle_idx, cycle in enumerate(cycles):
        binary_idx = format(cycle_idx, f'0{math.ceil(math.log2(len(cycles)))}b')  # Binary encoding of the cycle index
        for number in cycle:
            ctrl_states = ''.join(format(int(digit), '02b') for digit in number)
            # For each bit in the binary index, add control logic to the corresponding ancilla qubit
            for bit_pos, bit in enumerate(binary_idx):
                if bit == '1':
                    cgate = base_gate.control(num_ctrl_qubits=len(ctrl_states), ctrl_state=ctrl_states)
                    oracle.append(cgate, qr1[:len(ctrl_states)] + [qr2[bit_pos]])

    for qubit in range(2 * n, math.ceil(math.log2(len(cycles)))):
        key_string2 = ''.join(format(int(digit), '02b') for digit in key_string)
        if key_string2[qubit - n] == "1":
            oracle.x(qubit)
    return oracle_gate

def create_simon_ternary_circuit(n, oracle_as_gate):
    def gh():
        """
        Generate a generalized Hadamard unitary matrix suitable for quantum computation for a given base.

        Parameters:
        - base (int): The base for the generalized Hadamard matrix. For example, base 3 corresponds to the ternary system.

        Returns:
        - Operator: A Qiskit Operator representing the generalized Hadamard matrix.

        Examples:
        For base 3, the generalized Hadamard matrix is constructed using the 3rd root of unity.

        >>> gh(3)
        Operator([
            [ 0.57735027+0.j,  0.57735027+0.j,  0.57735027+0.j,  0.+0.j],
            [ 0.57735027+0.j,  0.28867513-0.5j, -0.28867513+0.5j,  0.+0.j],
            [ 0.57735027+0.j, -0.28867513+0.5j,  0.28867513-0.5j,  0.+0.j],
            [ 0.+0.j,         0.+0.j,          0.+0.j,          1.+0.j]
        ])

        This matrix can be used to transform a set of qubits prepared in the computational basis
        into a superposition state corresponding to the generalized Hadamard transform.
        """
        # Compute the primitive root of unity for the specified base
        omega = np.exp(2 * np.pi * 1j / 3)

        # The matrix dimension is the smallest power of 2 greater than or equal to the base
        m = int(np.ceil(np.log2(3)))
        matrix_size = 2 ** m

        # Initialize the unitary matrix
        U = np.zeros((matrix_size, matrix_size), dtype=complex)

        # Fill the top-left (base x base) block with powers of the root of unity
        for i in range(3):
            for j in range(3):
                U[i, j] = omega ** (i * j) / np.sqrt(3)

        # Ensure the matrix is unitary by filling in identity in the bottom-right
        for i in range(3, matrix_size):
            U[i, i] = 1

        return Operator(U)


    def My_gh_gate(n):
        gh_circuit = QuantumCircuit(2 * n)

        for i in range(n):
            gh_circuit.unitary(gh(), [2 * i + j for j in range(2)])

        gh_circuit = transpile(gh_circuit, basis_gates=['u1', 'u2', 'u3', 'cx'])

        gh_gate = gh_circuit.to_gate()
        gh_gate.name = "GH"

        return gh_gate


    def My_inverse_gh_gate(n):
        gh_circuit = QuantumCircuit(2 * n)

        for i in range(n):
            gh_circuit.unitary(gh().adjoint(), [2 * i + j for j in range(2)])

        gh_circuit = transpile(gh_circuit, basis_gates=['u1', 'u2', 'u3', 'cx'])

        gh_gate = gh_circuit.to_gate()
        gh_gate.name = "IGH"

        return gh_gate

    cycles = 3 ** n / 3

    # Create a quantum circuit on 2n+ceil(log2(cycles))) qubit
    simon_ternary_circuit = QuantumCircuit(2 * n + math.ceil(math.log2(cycles)), 2 * n)

    # Initialize the first register to the uniform superposition state
    simon_ternary_circuit.append(My_gh_gate(n), range(2 * n))

    # Append the Generalized Simon's oracle
    simon_ternary_circuit.append(oracle_as_gate, range(2 * n + math.ceil(math.log2(cycles))))

    # Apply the inverse of the Generalized H-gate to the first register
    simon_ternary_circuit.append(My_inverse_gh_gate(n), range(2 * n))

    # Measure the first register
    simon_ternary_circuit.measure(range(2 * n), range(2 * n))

    return simon_ternary_circuit


def substract_oracle_from_simon_ternary_qasm(qasm_str):
    import re


    lines = qasm_str.strip().splitlines()
    in_gate = False
    current_gate_name = ""
    buffer = []
    result_lines = []

    for line in lines:
        stripped = line.strip()


        if stripped.startswith("OPENQASM") and any("OPENQASM" in l for l in result_lines):
            continue
        if stripped == 'include "stdgates.inc";' and any('include "stdgates.inc";' in l for l in result_lines):
            continue

        if stripped.startswith("gate "):
            in_gate = True
            current_gate_name = stripped.split()[1]
            buffer = [line]
            continue

        if in_gate:
            buffer.append(line)
            if "}" in stripped:
                in_gate = False
                if current_gate_name == "GH":
                    result_lines.extend(buffer)
            continue

        result_lines.append(line)

    final_lines = []
    inserted = False
    for line in result_lines:
        final_lines.append(line)
        if line.strip() == 'include "stdgates.inc";' and not inserted:
            final_lines.append('include "oracle.inc";')
            inserted = True

    cleaned = '\n'.join(final_lines)
    cleaned = re.sub(r'\n\s*\n+', '\n', cleaned).strip()

    return cleaned



def run_simon_ternary_circuit(simon_circuit, n, shots=100):
    def binary_to_ternary(binary_str):
        return ''.join(str(int(binary_str[i:i+2], 2)) for i in range(0, len(binary_str), 2))

    def mod3(x):
        return S(x % 3)

    def rref_mod3(M):
        M = M.applyfunc(mod3)
        rows, cols = M.shape
        r = 0
        pivot_cols = []
        for c in range(cols):
            pivot_row = None
            for ri in range(r, rows):
                if M[ri, c] != 0:
                    pivot_row = ri
                    break
            if pivot_row is None:
                continue
            if pivot_row != r:
                M.row_swap(pivot_row, r)
            pivot_val = M[r, c]
            if pivot_val != 1:
                inv_pivot_val = mod3(pow(pivot_val, -1, 3))
                for j in range(cols):
                    M[r, j] = mod3(inv_pivot_val * M[r, j])
            for ri in range(rows):
                if ri != r and M[ri, c] != 0:
                    multiplier = M[ri, c]
                    for j in range(cols):
                        M[ri, j] = mod3(M[ri, j] - multiplier * M[r, j])
            pivot_cols.append(c)
            r += 1
            if r == rows:
                break
        return M, pivot_cols

    aer_sim = AerSimulator()
    equations = []
    iteration = 0
    while iteration < 10:
        circ = transpile(simon_circuit, aer_sim)
        results = aer_sim.run(circ, shots=shots).result()
        counts = results.get_counts()
        for result, count in counts.items():
            if result != "0" * (2 * n):
                ternary_result = binary_to_ternary(result)
                y = [int(digit) for digit in ternary_result]
                equations.append(y)
        if equations:
            M = Matrix(equations).applyfunc(mod3).T
            M_I = Matrix(np.hstack([M, np.eye(M.shape[0], dtype=int)]))
            M_I_rref = rref_mod3(M_I)
            M_I_final = M_I_rref[0].applyfunc(lambda x: x % 3)
            for i in range(M_I_final.rows):
                if all(mod3(val) == 0 for val in M_I_final.row(i)[:M.cols]):
                    solution_vector = [int(M_I_final.row(i)[j]) for j in range(M.cols, M_I_final.cols)]
                    result_s = ''.join(str(x) for x in solution_vector)
                    return result_s
        iteration += 1
    return '0' * n

if __name__ == "__main__":
    n = 3
    secret_string = '12001'
    key_string = '20100'
    oracle_gate = create_simon_ternary_oracle_as_gate(n, secret_string, key_string)
    full_circuit = create_simon_ternary_circuit(n, oracle_gate)
    full_circ_qasm = circuit_to_qasm_str(full_circuit)
    without_oracle = substract_oracle_from_simon_ternary_qasm(full_circ_qasm)
    print(without_oracle)
    print(run_simon_ternary_circuit(full_circuit, n))
