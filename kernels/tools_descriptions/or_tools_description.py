or_tools_description = {
    "module": "or_tools",
    "description": (
        "This module provides a set of tools for constructing a quantum circuit that performs a logical OR operation. "
        "It includes helper functions for creating input and output registers, building the circuit with an OR gate, "
        "and converting the final circuit to a QASM string."
    ),
    "functions": [
        {
            "name": "circuit_to_qasm_str",
            "signature": "circuit_to_qasm_str(circuit: QuantumCircuit) -> str",
            "description": "Converts a Qiskit QuantumCircuit into its QASM 3.0 string representation."
        },
        {
            "name": "create_input_registers",
            "signature": "create_input_registers(n: int) -> QuantumRegister",
            "description": "Creates and returns a quantum register of size n, named 'in', to be used as the inputs for the OR gate."
        },
        {
            "name": "create_output_register",
            "signature": "create_output_register() -> QuantumRegister",
            "description": "Creates and returns a single-qubit quantum register, named 'out', to store the output of the OR gate."
        },
        {
            "name": "create_or_circuit",
            "signature": "create_or_circuit(inputs: QuantumRegister, out: QuantumRegister, n: int) -> QuantumCircuit",
            "description": "Constructs a quantum circuit that performs a logical OR operation on n input qubits. The result is stored in the single output qubit. This is achieved using Qiskit's built-in OrGate."
        }
    ]
}