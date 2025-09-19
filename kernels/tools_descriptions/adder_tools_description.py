adder_tools_description = {
    "module": "adder_tools",
    "description": (
        "This module provides tools to construct a quantum full adder circuit using Qiskit. "
        "It includes functions for creating the necessary quantum registers, "
        "assembling the final adder circuit, and converting the circuit to a QASM string."
    ),
    "functions": [
        {
            "name": "circuit_to_qasm_str",
            "signature": "circuit_to_qasm_str(circuit: QuantumCircuit) -> str",
            "description": "Converts a Qiskit QuantumCircuit into its QASM 3.0 string representation."
        },
        {
            "name": "create_input_registers",
            "signature": "create_input_registers(n: int) -> tuple[QuantumRegister, QuantumRegister, QuantumRegister]",
            "description": (
                "Creates and returns three quantum registers required for an adder circuit: register 'a' of size n, "
                "register 'b' of size n, and a carry-in register 'cin' of size 1."
            )
        },
        {
            "name": "create_carryout_register",
            "signature": "create_carryout_register() -> QuantumRegister",
            "description": "Creates and returns a quantum register 'cout' of size 1 for the carry-out bit."
        },
        {
            "name": "create_adder_circuit",
            "signature": "create_adder_circuit(n: int, a: QuantumRegister, b: QuantumRegister, cin: QuantumRegister, cout: QuantumRegister) -> QuantumCircuit",
            "description": (
                "Constructs a quantum circuit for an n-bit full adder using the provided input registers "
                "('a', 'b', 'cin') and the carry-out register ('cout'). The circuit utilizes Qiskit's FullAdderGate."
            )
        }
    ]
}