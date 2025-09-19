cluster_tools_description = {
    "module": "cluster_tools",
    "description": (
        "This module provides a set of tools for creating a cluster state quantum circuit. "
        "It includes helper functions for initializing the circuit and its registers, applying the initial Hadamard gates, "
        "and entangling the qubits with a linear chain of Controlled-Z gates."
    ),
    "functions": [

        {
            "name": "initilize_circuit",
            "signature": "initilize_circuit(n: int) -> tuple[QuantumCircuit, QuantumRegister]",
            "description": "Creates and returns a QuantumCircuit and a QuantumRegister of n qubits, named 'q'."
        },
        {
            "name": "apply_h_gates",
            "signature": "apply_h_gates(qc: QuantumCircuit, q: QuantumRegister, n: int) -> QuantumCircuit",
            "description": "Applies a Hadamard (H) gate to each of the n qubits in the provided quantum register."
        },
        {
            "name": "apply_cz_gates",
            "signature": "apply_cz_gates(qc: QuantumCircuit, q: QuantumRegister, n: int) -> QuantumCircuit",
            "description": "Applies a Controlled-Z (CZ) gate between each adjacent qubit (q[i], q[i+1]) in the register, creating a linear entanglement pattern."
        },
        {
            "name": "circuit_to_qasm_str",
            "signature": "circuit_to_qasm_str(circuit: QuantumCircuit) -> str",
            "description": "Converts a Qiskit QuantumCircuit into its QASM 3.0 string representation."
        }
    ]
}