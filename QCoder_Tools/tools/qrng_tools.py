# tools needed for qrng algorithm
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.qasm3 import dump
from qiskit_aer import AerSimulator
from scipy.stats import chisquare, entropy
from io import StringIO

def generate_rng_circuit(n):
    """Generate a Quantum Random Number Generator (QRNG) circuit with n qubits."""
    circuit = QuantumCircuit(n, n)
    circuit.h(range(n))
    circuit.measure(range(n), range(n))
    return circuit

def circuit_to_qasm_string(circuit):
    """Convert a QuantumCircuit to QASM string."""
    buf = StringIO()
    dump(circuit, buf)
    return buf.getvalue()

def run_rng_and_get_random_bits(circuit, shots=1):
    """Run the QRNG circuit and get a list of random bitstrings."""
    aer_sim = AerSimulator()
    circ = transpile(circuit, aer_sim)
    result = aer_sim.run(circ, shots=shots).result()
    counts = result.get_counts()
    random_bitstrings = list(counts.keys())
    return random_bitstrings

def frequency_analysis(bitstrings, bit_length):
    """Perform a chi-squared frequency test on the random bitstrings."""
    num_outcomes = 2 ** bit_length
    observed_counts = [0] * num_outcomes
    for number in bitstrings:
        index = int(number, 2)
        observed_counts[index] += 1
    expected_count = len(bitstrings) / num_outcomes
    expected_counts = [expected_count] * num_outcomes
    chi2_stat, p_value = chisquare(observed_counts, expected_counts)
    return chi2_stat, p_value

def autocorrelation_analysis(bitstrings):
    """Compute the autocorrelation coefficient of the random bitstrings."""
    values = np.array([int(number, 2) for number in bitstrings])
    mean = np.mean(values)
    autocorr = np.correlate(values - mean, values - mean, mode="full")
    mid = len(autocorr) // 2
    autocorr = autocorr[mid:]
    autocorr /= autocorr[0]  # Normalize
    return autocorr[1]

def entropy_analysis(bitstrings):
    """Compute the entropy (in bits) of the random bitstrings."""
    values, counts = np.unique(bitstrings, return_counts=True)
    probabilities = counts / counts.sum()
    return entropy(probabilities, base=2)

if __name__ == "__main__":
    n = 4
    shots = 100
    circuit = generate_rng_circuit(n)
    qasm_str = circuit_to_qasm_string(circuit)
    print("Generated QASM:")
    print(qasm_str)

    random_bits = run_rng_and_get_random_bits(circuit, shots=shots)
    print(f"Random bitstrings ({shots} shots): {random_bits}")

    chi2_stat, p_value = frequency_analysis(random_bits, n)
    autocorr = autocorrelation_analysis(random_bits)
    entropy_val = entropy_analysis(random_bits)

    print(f"Chi-squared stat: {chi2_stat}, p-value: {p_value}")
    print(f"Autocorrelation coefficient: {autocorr}")
    print(f"Entropy: {entropy_val} bits")
