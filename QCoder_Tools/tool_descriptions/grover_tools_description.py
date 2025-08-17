grover_tools_description = {
    "module": "grover_tools",
    "description": (
        "This module provides Grover's algorithm tools, including functions to generate Grover circuits, "
        "generate oracle gates, combine circuits, convert circuits to QASM strings, and test both Grover circuits "
        "and oracles. All functions are designed to work with Qiskit and AerSimulator."
    ),
    "functions": [
        {
            "name": "create_grover_oracle",
            "signature": "create_grover_oracle(n: int, marked_state: str) -> Gate",
            "description": (
                "Creates a Grover oracle gate for a given number of qubits (n) and the target marked state "
                "(as a bit string). The returned Gate can be attached to a QuantumCircuit."
            )
        },
        {
            "name": "create_grover_oracle_as_circuit",
            "signature": "create_grover_oracle_as_circuit(n: int, marked_state: str) -> QuantumCircuit",
            "description": (
                "Creates a Grover oracle Circuit for a given number of qubits (n) and the target marked state "
                "The returned oracle circuit can be turned to a printable string via the function called circuit_to_qasm_str."
            )
        },
        {
            "name": "generate_grover_circuit",
            "signature": "generate_grover_circuit(n: int) -> QuantumCircuit",
            "description": (
                "Generates a bare Grover's algorithm circuit (without oracle) for the given number of qubits (n). "
                "The circuit includes Hadamard initialization, multiple Grover iterations (only diffusion), and measurements."
            )
        },
        {
            "name": "create_diffusion_operator",
            "signature": "create_diffusion_operator(n: int) -> Gate",
            "description": (
                "Creates the diffusion (inversion about the mean) operator used in Grover's algorithm "
                "for a given number of qubits (n)."
            )
        },
        {
            "name": "combine_oracle_with_circuit",
            "signature": "combine_oracle_with_circuit(circuit: QuantumCircuit, oracle_gate: Gate, num_iterations: int = None) -> QuantumCircuit",
            "description": (
                "Combines a provided bare circuit with an oracle gate, applying the oracle and diffusion operator "
                "for the calculated or specified number of Grover iterations."
            )
        },
        {
            "name": "circuit_to_qasm_str",
            "signature": "circuit_to_qasm_str(circuit: QuantumCircuit) -> str",
            "description": "Converts a Qiskit QuantumCircuit into its QASM 3.0 string representation."
        },
        {
            "name": "test_grover_circuit",
            "signature": "test_grover_circuit(circuit_template: QuantumCircuit, n: int, shots: int = 100) -> bool",
            "description": (
                "Tests the bare Grover circuit (without oracle) by combining it with multiple randomly generated oracles. "
                "Returns whether all tests are passed"
            )
        },
        {
            "name": "test_grover_oracle",
            "signature": "test_grover_oracle(n: int, oracle_gate: Gate, shots: int = 100) -> str",
            "description": (
                "Tests a given Grover oracle by embedding it into a complete Grover circuit "
                "and returning the most frequently predicted marked state."
            )
        }
    ]
}
