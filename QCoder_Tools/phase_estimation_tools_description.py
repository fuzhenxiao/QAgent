phase_estimation_tools_description = {
    "module": "phase_estimation_tools",
    "description": (
        "This module provides tools for building and testing the Quantum Phase Estimation (QPE) algorithm. "
        "It includes functions to construct controlled unitary gates (CU), eigenstate gates (Psi), QPE circuits, "
        "extract QASM strings, and simulate the circuit using AerSimulator to retrieve the estimated phase."
    ),
    "functions": [
        {
            "name": "generate_random_theta_based_on_n",
            "signature": "generate_random_theta_based_on_n(n: int) -> Tuple[float, float]",
            "description": (
                "Generates a random angle theta and its normalized phase fraction (theta / 2π) "
                "based on the number of counting qubits (n)."
            )
        },
        {
            "name": "My_U_gate",
            "signature": "My_U_gate(theta: float) -> Gate",
            "description": (
                "Constructs a controlled-U gate (CU_0) that applies a phase shift of theta "
                "to the target qubit when the control qubit is 1."
            )
        },
        {
            "name": "My_psi_gate",
            "signature": "My_psi_gate() -> Gate",
            "description": (
                "Generates the Psi eigenstate gate used as input to the phase estimation circuit. "
                "This version prepares the eigenstate |1⟩."
            )
        },
        {
            "name": "create_phase_estimation_circuit",
            "signature": "create_phase_estimation_circuit(n: int, cu_gate: Gate, psi_gate: Gate) -> QuantumCircuit",
            "description": (
                "Constructs the complete Quantum Phase Estimation (QPE) circuit using n counting qubits, "
                "a controlled unitary gate, and an eigenstate input gate. The circuit includes Hadamard preparation, "
                "controlled-U applications, inverse QFT, and measurement."
            )
        },
        {
            "name": "circuit_to_qasm_str",
            "signature": "circuit_to_qasm_str(circuit: QuantumCircuit) -> str",
            "description": (
                "Converts a given Qiskit QuantumCircuit into a QASM 3.0 formatted string."
            )
        },
        {
            "name": "gate_to_qasm_str",
            "signature": "gate_to_qasm_str(gate: Gate) -> str",
            "description": (
                "Converts a given Qiskit Gate object (e.g., CU or Psi) into a QASM 3.0 formatted string."
            )
        },
        {
            "name": "substract_oracle_from_phase_estimation_qasm",
            "signature": "substract_oracle_from_phase_estimation_qasm(qasm_str: str) -> str",
            "description": (
                "Removes the definitions of CU and Psi gates from the QASM string and inserts "
                "\"include \\\"oracle.inc\\\"\" instead. This is used to modularize the circuit and externalize the oracle."
            )
        },
        {
            "name": "run_phase_estimation_circuit",
            "signature": "run_phase_estimation_circuit(phase_circuit: QuantumCircuit) -> float",
            "description": (
                "Simulates the QPE circuit using Qiskit's AerSimulator backend and returns the estimated phase "
                "as a float in the interval [0, 1)."
            )
        }
    ]
}
