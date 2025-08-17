# tools needed for qft algorithm
from qiskit import QuantumCircuit,transpile
from qiskit_aer import AerSimulator
from qiskit.circuit.library import QFT
import numpy as np
from qiskit.qasm3 import dump
from io import StringIO
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import QFT
from qiskit_aer import AerSimulator
import numpy as np

def create_qft_circuit(n):
    qc = QuantumCircuit(n, n)
    qc.x(0)  
    qc.append(QFT(num_qubits=n, do_swaps=False), range(n))
    qc.measure(range(n), range(n))
    return qc

def circuit_to_qasm_str(circuit):
    buf = StringIO()
    decomposed = circuit
    while True:
        new_circuit = decomposed.decompose()
        if new_circuit == decomposed:
            break
        decomposed = new_circuit
    dump(decomposed, buf)
    return buf.getvalue()

def run_qft(qc, shots=8192):
    aer_sim = AerSimulator()
    qc_compiled = transpile(qc, aer_sim)
    result = aer_sim.run(qc_compiled, shots=shots).result()
    counts = result.get_counts()
    return counts

def theoretical_qft_probabilities(n):
    vec = np.zeros(2 ** n, dtype=complex)
    vec[1] = 1  # |1⟩
    fft = np.fft.fft(vec) / np.sqrt(2 ** n)
    probs = np.abs(fft) ** 2
    prob_dict = {format(i, f'0{n}b'): probs[i] for i in range(2 ** n)}
    return prob_dict

def compare_distributions(theory, measured, shots):
    mse = 0
    for bitstring, theo_prob in theory.items():
        meas_prob = measured.get(bitstring, 0) / shots
        mse += (theo_prob - meas_prob) ** 2
    mse /= len(theory)
    return mse

if __name__ == "__main__":
    n = 3
    shots = 8192
    qc = create_qft_circuit(n)
    print(circuit_to_qasm_str(qc))
    counts = run_qft(qc, shots=shots)

    # 理论分布
    theory_probs = theoretical_qft_probabilities(n)

    # 比较
    mse = compare_distributions(theory_probs, counts, shots)

    print(f"Theoretical probabilities:\n{theory_probs}")
    print(f"Measured counts:\n{counts}")
    print(f"Mean Squared Error (MSE) between theory and measurement: {mse:.6f}")

    if mse < 0.01:
        print("QFT circuit matches theoretical distribution (low error).")
    else:
        print("QFT circuit shows noticeable deviation (high error).")
