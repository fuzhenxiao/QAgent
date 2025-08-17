deutsch_jozsa_tools_description = {
    "module": "deutsch_jozsa_tools",
    "description": (
        "This module provides Deutsch-Jozsa algorithm tools, including functions to generate DJ circuits, "
        "generate oracle gates, combine circuits, convert circuits to QASM strings, and test complete DJ circuits. "
        "All functions are designed to work with Qiskit and AerSimulator."
    ),
    "functions": [
        {
            "name": "create_deutsch_jozsa_oracle_as_gate",
            "signature": "create_deutsch_jozsa_oracle_as_gate(n: int, is_constant: bool, key_string: str) -> Gate",
            "description": (
                "Creates a Deutsch-Jozsa oracle gate for a given number of input qubits (n), specifying whether the "
                "oracle is constant or balanced, and the key string pattern. The returned Gate can be attached "
                "to a QuantumCircuit."
            )
        },
        {
            "name": "create_deutsch_jozsa_oracle_as_circuit",
            "signature": "create_deutsch_jozsa_oracle_as_circuit(n: int, is_constant: bool, key_string: str) -> QuantumCircuit",
            "description": (
                "Creates a Deutsch-Jozsa oracle circuit for the given number of input qubits (n), constant/balanced "
                "flag, and key string. The returned circuit can be converted to a printable QASM string using "
                "the circuit_to_qasm_str function."
            )
        },
        {
            "name": "create_deutsch_jozsa_circuit",
            "signature": "create_deutsch_jozsa_circuit(n: int, oracle_as_gate: Gate) -> QuantumCircuit",
            "description": (
                "Generates the complete Deutsch-Jozsa algorithm circuit for the given number of input qubits (n), "
                "using the provided oracle gate. The circuit includes initialization, oracle application, "
                "final Hadamard gates, and measurements."
            )
        },
        {
            "name": "circuit_to_qasm_str",
            "signature": "circuit_to_qasm_str(circuit: QuantumCircuit) -> str",
            "description": "Converts a Qiskit QuantumCircuit into its QASM 3.0 string representation."
        },
        {
            "name": "substract_oracle_from_deutsch_jozsa_qasm",
            "signature": "substract_oracle_from_deutsch_jozsa_qasm(deutsch_jozsa_qasm: str) -> str",
            "description": (
                "Replaces the oracle definition inside a Deutsch-Jozsa QASM string with a placeholder include "
                "statement (e.g., include \"oracle.inc\"). Useful for separating the oracle definition from the circuit "
                "and outputting a bare QASM circuit for the Deutsch-Jozsa algorithm alone."
            )
        },
        {
            "name": "run_deutsch_jozsa_circuit",
            "signature": "run_deutsch_jozsa_circuit(circuit: QuantumCircuit) -> str",
            "description": (
                "Executes the provided Deutsch-Jozsa circuit on the Qiskit AerSimulator backend and returns whether "
                "the oracle is constant or balanced, based on the measured result."
            )
        }
    ]
}
