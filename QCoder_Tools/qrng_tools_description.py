qrng_tools_description = {
    "module": "qrng_tools",
    "description": (
        "This module provides Quantum Random Number Generator (QRNG) tools, including functions to generate QRNG circuits, "
        "convert circuits to QASM strings, run the circuits to obtain random bitstrings, and perform statistical analyses "
        "such as chi-squared frequency tests, autocorrelation checks, and entropy calculations. All functions are designed "
        "to work with Qiskit and AerSimulator."
    ),
    "functions": [
        {
            "name": "generate_rng_circuit",
            "signature": "generate_rng_circuit(n: int) -> QuantumCircuit",
            "description": (
                "Generates a QRNG circuit using n qubits, applying Hadamard gates to create superposition "
                "and measuring the qubits to obtain random bitstrings."
            )
        },
        {
            "name": "circuit_to_qasm_string",
            "signature": "circuit_to_qasm_string(circuit: QuantumCircuit) -> str",
            "description": "Converts a Qiskit QuantumCircuit into its QASM 3.0 string representation."
        },
        {
            "name": "run_rng_and_get_random_bits",
            "signature": "run_rng_and_get_random_bits(circuit: QuantumCircuit, shots: int = 1) -> List[str]",
            "description": (
                "Runs the provided QRNG circuit on the Qiskit AerSimulator backend and returns a list of random bitstrings "
                "collected over the specified number of shots."
            )
        },
        {
            "name": "frequency_analysis",
            "signature": "frequency_analysis(bitstrings: List[str], bit_length: int) -> Tuple[float, float]",
            "description": (
                "Performs a chi-squared frequency test on the collected random bitstrings to assess their uniformity, "
                "returning the chi-squared statistic and p-value."
            )
        },
        {
            "name": "autocorrelation_analysis",
            "signature": "autocorrelation_analysis(bitstrings: List[str]) -> float",
            "description": (
                "Computes the autocorrelation coefficient of the random bitstrings to evaluate correlation between samples."
            )
        },
        {
            "name": "entropy_analysis",
            "signature": "entropy_analysis(bitstrings: List[str]) -> float",
            "description": (
                "Calculates the entropy (in bits) of the random bitstrings, representing their randomness quality."
            )
        }
    ]
}
