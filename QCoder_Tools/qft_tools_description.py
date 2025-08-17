qft_tools_description = {
    "module": "qft_tools",
    "description": (
        "This module provides Quantum Fourier Transform (QFT) tools, including functions to generate QFT circuits, "
        "convert circuits to QASM strings, run simulations to obtain measured distributions, compute theoretical QFT probabilities, "
        "and compare theoretical and measured distributions using mean squared error (MSE). All functions are designed to work with Qiskit and AerSimulator."
    ),
    "functions": [
        {
            "name": "create_qft_circuit",
            "signature": "create_qft_circuit(n: int) -> QuantumCircuit",
            "description": (
                "Generates a QFT circuit on n qubits, preparing the initial |1⟩ state and applying the QFT without final swaps, "
                "followed by measurements."
            )
        },
        {
            "name": "circuit_to_qasm_str",
            "signature": "circuit_to_qasm_str(circuit: QuantumCircuit) -> str",
            "description": (
                "Converts a (decomposed) Qiskit QuantumCircuit into its QASM 3.0 string representation, ensuring all composite gates "
                "are broken down into basic gates."
            )
        },
        {
            "name": "run_qft",
            "signature": "run_qft(qc: QuantumCircuit, shots: int = 8192) -> Dict[str, int]",
            "description": (
                "Runs the provided QFT circuit on the Qiskit AerSimulator backend and returns a dictionary of measured bitstring counts."
            )
        },
        {
            "name": "theoretical_qft_probabilities",
            "signature": "theoretical_qft_probabilities(n: int) -> Dict[str, float]",
            "description": (
                "Computes the theoretical probability distribution for the QFT applied to the |1⟩ state on n qubits, "
                "returning a dictionary mapping bitstrings to their probabilities."
            )
        },
        {
            "name": "compare_distributions",
            "signature": "compare_distributions(theory: Dict[str, float], measured: Dict[str, int], shots: int) -> float",
            "description": (
                "Calculates the mean squared error (MSE) between the theoretical probabilities and the measured distribution, "
                "based on the given number of shots."
            )
        }
    ]
}
