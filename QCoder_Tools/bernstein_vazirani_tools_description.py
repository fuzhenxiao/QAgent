bernstein_vazirani_tools_description = {
    "module": "bernstein_vazirani_tools",
    "description": (
        "This module provides Bernstein-Vazirani algorithm tools, including functions to generate BV circuits, "
        "generate oracle gates, combine circuits, convert circuits to QASM strings, and test complete BV circuits. "
        "All functions are designed to work with Qiskit and AerSimulator."
    ),
    "functions": [
        {
            "name": "create_bernstein_vazirani_oracle_as_gate",
            "signature": "create_bernstein_vazirani_oracle_as_gate(n: int, secret_string: str) -> Gate",
            "description": (
                "Creates a Bernstein-Vazirani oracle gate for a given number of qubits (n) and the secret string "
                "(as a bit string). The returned Gate can be attached to a QuantumCircuit."
            )
        },
        {
            "name": "create_bernstein_vazirani_oracle_as_circuit",
            "signature": "create_bernstein_vazirani_oracle_as_circuit(n: int, secret_string: str) -> QuantumCircuit",
            "description": (
                "Creates a Bernstein-Vazirani oracle circuit for a given number of qubits (n) and the secret string. "
                "The returned circuit can be converted to a printable QASM string using the circuit_to_qasm_str function."
            )
        },
        {
            "name": "create_bernstein_vazirani_circuit",
            "signature": "create_bernstein_vazirani_circuit(n: int, oracle_as_gate: Gate) -> QuantumCircuit",
            "description": (
                "Generates the complete Bernstein-Vazirani algorithm circuit for the given number of qubits (n), "
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
            "name": "substract_oracle_from_bernstein_vazirani_qasm",
            "signature": "substract_oracle_from_bernstein_vazirani_qasm(bernstein_vazirani_qasm: str) -> str",
            "description": (
                "Replaces the oracle definition inside a Bernstein-Vazirani QASM string with a placeholder include "
                "statement (e.g., include \"oracle.inc\"). Useful for separating oracle definition from circuit"
                "and outputs bare qasm circuit for bernstein vazinari circuit alone."
            )
        },
        {
            "name": "run_bernstein_vazirani_circuit",
            "signature": "run_bernstein_vazirani_circuit(circuit: QuantumCircuit) -> str",
            "description": (
                "Executes the provided Bernstein-Vazirani circuit on the Qiskit AerSimulator backend and returns "
                "the most frequently measured bitstring (i.e., the discovered secret string)."
            )
        }
    ]
}
