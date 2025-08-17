ghz_tools_description = {
    "module": "ghz_tools",
    "description": (
        "This module provides GHZ (Greenberger-Horne-Zeilinger) state tools, including functions to generate GHZ circuits, "
        "convert circuits to QASM strings, simulate circuits to obtain statevectors, compare simulated results with the ideal GHZ state, "
        "and extract qubit indices. All functions are designed to work with Qiskit and AerSimulator."
    ),
    "functions": [
        {
            "name": "generate_ghz_circuit",
            "signature": "generate_ghz_circuit(n: int) -> QuantumCircuit",
            "description": (
                "Generates a GHZ state preparation circuit for the specified number of qubits (n). "
                "The circuit applies a Hadamard gate on the first qubit followed by a series of controlled-X gates."
                "Please mind that this function is CORRECT! and is sufficient to create a ghz circuit."
                "There is no need to create a new function"
            )
        },
        {
            "name": "circuit_to_qasm_string",
            "signature": "circuit_to_qasm_string(circuit: QuantumCircuit) -> str",
            "description": "Converts a Qiskit QuantumCircuit into its QASM 3.0 string representation."
        },
        {
            "name": "get_goal_ghz_statevector",
            "signature": "get_goal_ghz_statevector(n: int) -> Statevector",
            "description": (
                "Returns the theoretical target GHZ statevector for n qubits, represented as an equal superposition "
                "of |00...0⟩ and |11...1⟩."
            )
        },
        {
            "name": "run_ghz_circuit_and_get_statevector",
            "signature": "run_ghz_circuit_and_get_statevector(circuit: QuantumCircuit) -> Statevector",
            "description": (
                "Runs the provided GHZ circuit on the Qiskit AerSimulator backend (using the statevector method) "
                "and returns the resulting statevector."
            )
        },
        {
            "name": "check_ghz_equivalence",
            "signature": "check_ghz_equivalence(statevector: Statevector, n: int, rtol: float = 1e-3) -> bool",
            "description": (
                "Checks if the provided statevector is equivalent to the ideal n-qubit GHZ state, within a relative tolerance."
            )
        },
        {
            "name": "extract_qubit_indices",
            "signature": "extract_qubit_indices(circuit: QuantumCircuit) -> List[int]",
            "description": "Returns a list of qubit indices used in the provided circuit."
        }
    ]
}
