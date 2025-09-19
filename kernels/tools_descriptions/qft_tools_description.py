qft_tools_description = {
    "module": "qft_tools",
    "description": (
        "This module provides a set of tools for constructing a Quantum Fourier Transform (QFT) circuit. "
        "It includes functions to initialize a circuit with classical and quantum bits, apply the QFT gate, "
        "add a measurement layer, and convert the fully decomposed circuit into a QASM string."
    ),
    "functions": [
        {
            "name": "initialize_qft_circuit",
            "signature": "initialize_qft_circuit(n: int) -> QuantumCircuit",
            "description": "Initializes and returns a QuantumCircuit with n quantum bits and n classical bits."
        },
        {
            "name": "apply_qft_gate",
            "signature": "apply_qft_gate(qc: QuantumCircuit, n: int) -> QuantumCircuit",
            "description": "Applies the Quantum Fourier Transform (QFT) operation to the first n qubits of the circuit using Qiskit's built-in QFT gate."
        },
        {
            "name": "apply_measure_layer",
            "signature": "apply_measure_layer(qc: QuantumCircuit, n: int) -> QuantumCircuit",
            "description": "Adds a measurement operation to the circuit, mapping each of the n quantum bits to its corresponding classical bit."
        },
        {
            "name": "circuit_to_qasm_str",
            "signature": "circuit_to_qasm_str(circuit: QuantumCircuit) -> str",
            "description": "Fully decomposes a Qiskit QuantumCircuit into its elementary gates and then converts it into its QASM 3.0 string representation. This is useful for viewing the underlying gates of high-level objects like the QFT gate."
        }
    ]
}