w_state_tools_description = {
    "module": "w_state_tools",
    "description": (
        "This module provides tools for generating and validating W states, including functions to construct W state circuits, "
        "convert circuits to QASM strings, simulate circuits to obtain statevectors, generate ideal W statevectors, "
        "compare simulated and ideal states, and extract qubit indices involved. All functions are designed to work with Qiskit and AerSimulator."
    ),
    "functions": [
        {
            "name": "generate_w_state_circuit",
            "signature": "generate_w_state_circuit(n: int) -> QuantumCircuit",
            "description": (
                "Generates a W state preparation circuit for the specified number of qubits (n), using RY and CZ gates "
                "followed by a sequence of CNOT operations."
            )
        },
        {
            "name": "circuit_to_qasm_string",
            "signature": "circuit_to_qasm_string(circuit: QuantumCircuit) -> str",
            "description": "Converts a Qiskit QuantumCircuit into its QASM 3.0 string representation."
        },
        {
            "name": "run_w_state_and_get_statevector",
            "signature": "run_w_state_and_get_statevector(circuit: QuantumCircuit) -> Statevector",
            "description": (
                "Runs the provided W state circuit on the Qiskit AerSimulator backend (using the statevector method) "
                "and returns the resulting statevector."
            )
        },
        {
            "name": "generate_goal_w_statevector",
            "signature": "generate_goal_w_statevector(n: int) -> Statevector",
            "description": (
                "Generates the theoretical W statevector for n qubits, representing an equal superposition over all single-excitation states."
            )
        },
        {
            "name": "compare_statevectors",
            "signature": "compare_statevectors(statevector: Statevector, goal_state: Statevector, rtol: float = 1e-3) -> bool",
            "description": (
                "Checks if the provided statevector is equivalent to the ideal W statevector within a specified relative tolerance."
            )
        },
        {
            "name": "extract_qubit_indices",
            "signature": "extract_qubit_indices(n: int) -> List[int]",
            "description": "Returns the list of qubit indices involved in the W state circuit."
        }
    ]
}
