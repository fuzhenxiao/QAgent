qrng_tools_description = {
    "module": "qrng_tools",
    "description": (
        "This module provides the necessary tools to construct a simple Quantum Random Number Generator (QRNG) circuit. "
        "It includes functions for initializing the circuit, applying Hadamard gates to create a uniform superposition, "
        "and measuring the qubits to generate random classical bits."
    ),
    "functions": [
        {
            "name": "initialize_rng_circuit",
            "signature": "initialize_rng_circuit(n: int) -> QuantumCircuit",
            "description": "Initializes and returns a QuantumCircuit with n quantum bits and n classical bits, setting up the foundation for an n-bit random number generator."
        },
        {
            "name": "apply_h_gates",
            "signature": "apply_h_gates(qc: QuantumCircuit, n: int) -> QuantumCircuit",
            "description": "Applies a Hadamard (H) gate to each of the n qubits. This places each qubit into a perfect superposition, where it has an equal probability of collapsing to 0 or 1 upon measurement."
        },
        {
            "name": "apply_measure_layer",
            "signature": "apply_measure_layer(qc: QuantumCircuit, n: int) -> QuantumCircuit",
            "description": "Adds a measurement operation to the circuit, which collapses the superposition of each qubit into a definite classical state (0 or 1), generating a random bit string."
        },
        {
            "name": "circuit_to_qasm_string",
            "signature": "circuit_to_qasm_string(circuit: QuantumCircuit) -> str",
            "description": "Converts a Qiskit QuantumCircuit into its QASM 3.0 string representation."
        }
    ]
}