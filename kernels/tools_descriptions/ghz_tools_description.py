ghz_tools_description = {
    "module": "ghz_tools",
    "description": (
        "This module provides tools for constructing a Greenberger-Horne-Zeilinger (GHZ) state quantum circuit. "
        "It includes functions to initialize the circuit, apply a Hadamard gate to create superposition, "
        "and apply CNOT gates to entangle the qubits."
    ),
    "functions": [
        {
            "name": "initialize_ghz_circuit",
            "signature": "initialize_ghz_circuit(n: int) -> QuantumCircuit",
            "description": "Initializes and returns a QuantumCircuit with n qubits."
        },
        {
            "name": "apply_one_h_gate",
            "signature": "apply_one_h_gate(circuit: QuantumCircuit) -> QuantumCircuit",
            "description": "Applies a single Hadamard (H) gate to the first qubit (q[0]) of the circuit to create a superposition."
        },
        {
            "name": "apply_cx_gates",
            "signature": "apply_cx_gates(circuit: QuantumCircuit, n: int) -> QuantumCircuit",
            "description": "Entangles the qubits by applying a Controlled-NOT (CX) gate from the first qubit (control) to every other qubit (target)."
        },
        {
            "name": "circuit_to_qasm_string",
            "signature": "circuit_to_qasm_string(circuit: QuantumCircuit) -> str",
            "description": "Converts a Qiskit QuantumCircuit into its QASM 3.0 string representation."
        }
    ]
}