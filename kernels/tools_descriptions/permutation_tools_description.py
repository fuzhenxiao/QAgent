permutation_tools_description = {
    "module": "permutation_tools",
    "description": (
        "This module offers tools for creating quantum circuits that apply a specific permutation to a set of qubits. "
        "It includes functions to generate a cyclic shift permutation pattern, initialize a template circuit, "
        "and implement the permutation logic using Qiskit's PermutationGate."
    ),
    "functions": [

        {
            "name": "make_shift_permutation_pattern",
            "signature": "make_shift_permutation_pattern(n: int) -> list[int]",
            "description": "Generates a permutation pattern for n qubits that represents a cyclic shift, where each qubit's state is moved to the next qubit's position (e.g., for n=4, the pattern is [1, 2, 3, 0])."
        },
        {
            "name": "create_permutation_template_circuit",
            "signature": "create_permutation_template_circuit(n: int) -> tuple[QuantumCircuit, QuantumRegister]",
            "description": "Creates and returns a blank QuantumCircuit and a QuantumRegister of n qubits to serve as a template for the permutation."
        },
        {
            "name": "implement_permutation_logic",
            "signature": "implement_permutation_logic(qc: QuantumCircuit, q: QuantumRegister, pattern: list) -> QuantumCircuit",
            "description": "Applies a permutation to the qubits in the provided circuit according to the specified pattern list, utilizing Qiskit's PermutationGate."
        },
        {
            "name": "circuit_to_qasm_str",
            "signature": "circuit_to_qasm_str(circuit: QuantumCircuit) -> str",
            "description": "Converts a Qiskit QuantumCircuit into its QASM 3.0 string representation."
        }
    ]
}