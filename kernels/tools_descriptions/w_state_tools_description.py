w_state_tools_description = {
    "module": "w_state_tools",
    "description": (
        "This module provides tools to construct a quantum circuit for generating the W-state, a specific class of multipartite entangled states. "
        "The process involves initializing the circuit, flipping one qubit, and then applying a series of custom rotation gates and CNOT gates to create the desired state."
    ),
    "functions": [
        {
            "name": "initialize_w_state_circuit",
            "signature": "initialize_w_state_circuit(n: int) -> QuantumCircuit",
            "description": "Initializes and returns a QuantumCircuit with n quantum bits and n classical bits."
        },
        {
            "name": "apply_one_x_gate",
            "signature": "apply_one_x_gate(qc: QuantumCircuit, n: int) -> QuantumCircuit",
            "description": "Applies a single X gate to the last qubit (q[n-1]), flipping its state from |0> to |1> to begin the W-state preparation."
        },
        {
            "name": "apply_F_gate",
            "signature": "apply_F_gate(qc: QuantumCircuit, n: int) -> QuantumCircuit",
            "description": "Applies a sequence of custom F-gates, which are composed of controlled rotations, to progressively entangle the qubits into the W-state superposition."
        },
        {
            "name": "apply_cx_gates",
            "signature": "apply_cx_gates(qc: QuantumCircuit, n: int) -> QuantumCircuit",
            "description": "Applies a cascading series of Controlled-NOT (CX) gates to finalize the entanglement structure of the W-state."
        },
        {
            "name": "circuit_to_qasm_string",
            "signature": "circuit_to_qasm_string(circuit: QuantumCircuit) -> str",
            "description": "Converts a Qiskit QuantumCircuit into its QASM 3.0 string representation."
        }
    ]
}