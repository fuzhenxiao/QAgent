grover_tools_description = {
    "module": "grover_tools",
    "description": (
        "This module provides Grover's algorithm tools, including functions to generate Grover oracle gates, "
        "create complete Grover circuits, convert circuits to QASM strings, remove oracle definitions from QASM, "
        "and run the circuits to identify marked states. All functions are designed to work with Qiskit and AerSimulator."
    ),
    "functions": [
        {
            "name": "create_grover_oracle_as_gate",
            "signature": "create_grover_oracle_as_gate(n: int, marked_state: str) -> Gate",
            "description": (
                "Creates a Grover oracle gate for the specified number of qubits (n) and the marked bitstring. "
                "The returned Gate can be attached to a QuantumCircuit."
            )
        },
        {
            "name": "create_grover_oracle_as_circuit",
            "signature": "create_grover_oracle_as_circuit(n: int, marked_state: str) -> QuantumCircuit",
            "description": (
                "Creates a Grover oracle circuit for the specified number of qubits (n) and marked bitstring. "
                "The returned circuit can be converted to QASM using the circuit_to_qasm_str function."
            )
        },
        {
            "name": "create_grover_circuit",
            "signature": "create_grover_circuit(n: int, oracle_as_gate: Gate) -> QuantumCircuit",
            "description": (
                "Generates the complete Grover's algorithm circuit for the specified number of qubits (n), using "
                "the provided oracle gate. It includes Hadamard initialization, repeated oracle and diffusion applications, "
                "and final measurements."
            )
        },
        {
            "name": "circuit_to_qasm_str",
            "signature": "circuit_to_qasm_str(circuit: QuantumCircuit) -> str",
            "description": "Converts a Qiskit QuantumCircuit into its QASM 3.0 string representation."
        },
        {
            "name": "substract_oracle_from_grover_qasm",
            "signature": "substract_oracle_from_grover_qasm(grover_qasm: str) -> str",
            "description": (
                "Replaces the oracle definition inside a Grover QASM string with a placeholder include statement "
                "(e.g., include \"oracle.inc\"). Useful for separating the oracle definition from the circuit "
                "and outputting a bare Grover circuit."
            )
        },
        {
            "name": "run_grover_circuit",
            "signature": "run_grover_circuit(grover_circuit: QuantumCircuit, shots: int = 100) -> str",
            "description": (
                "Runs the provided Grover circuit on the Qiskit AerSimulator backend and returns the most frequently "
                "measured bitstring (i.e., the predicted marked state)."
            )
        }
    ]
}
