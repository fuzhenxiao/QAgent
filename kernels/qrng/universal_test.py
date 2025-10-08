from qiskit_aer import AerSimulator
from qiskit.qasm3 import loads
from scipy.stats import chisquare, entropy
import numpy as np
from qiskit import transpile


def frequency_test(data, bit_length):

    num_outcomes = 2**bit_length
    observed_counts = [0] * num_outcomes

    for number in data:
        index = int(number, 2)  
        observed_counts[index] += 1


    expected_count = len(data) / num_outcomes
    expected_counts = [expected_count] * num_outcomes


    chi2_stat, p_value = chisquare(observed_counts, expected_counts)
    return chi2_stat, p_value


def autocorrelation_test(data):
    values = np.array([int(number, 2) for number in data])
    mean = np.mean(values)
    autocorr = np.correlate(values - mean, values - mean, mode="full")
    mid = len(autocorr) // 2
    autocorr = autocorr[mid:]
    autocorr /= autocorr[0]
    return autocorr[1]


def entropy_test(data):
    values, counts = np.unique(data, return_counts=True)
    probabilities = counts / counts.sum()
    return entropy(probabilities, base=2)


def print_and_save(message, text):
    print(message)
    text.append(message)


def verify_qasm_syntax(qasm_code):
    try:
        return loads(qasm_code),'syntax correct'
    except Exception as e:
        print("QASM parsing failed:", e)
        return None,str(f'"QASM parsing failed. {e}')


def run_and_analyze(circuit, aer_sim):
    circ = transpile(circuit, aer_sim)
    result = aer_sim.run(circ, shots=1).result()
    counts = result.get_counts()
    random_number = list(counts.keys())[0]
    return random_number

def universal_check(qasm_string, n):

    circuit, rep = verify_qasm_syntax(qasm_string)
    if circuit is None:
        return False, 0, rep

    try:
        aer_sim = AerSimulator()
        trials =32
        data = []
        for _ in range(trials):
            data.append(run_and_analyze(circuit, aer_sim))
        
        chi2_stat, chi2_p = frequency_test(data, n)
        auto_corr = autocorrelation_test(data)
        entropy_val = entropy_test(data)
        
        chi2_score = chi2_p
        autocorr_score = min(1, max(0, 1 - abs(auto_corr)))
        entropy_score = min(1, max(0, entropy_val / (n - 1)))

        rng_valid = (chi2_score + autocorr_score + entropy_score) / 3
        
        if rng_valid > 0.5:
            return True, rng_valid, 'passed all tests'
        else:
            return False, rng_valid, 'Randomness lower than requirement'

    except Exception as e:
        return False, 0.0, str(e)

qrng_execute_description = """
qrng_execute(qasmstring, n) -> List[str]

Inputs:
  - qasmstring: str
      OpenQASM 3.0 source code for a quantum random number generator (QRNG).

  - n: int
      Bit-length of the random numbers to generate (number of measured qubits).

Behavior:
  1) Parses qasmstring and verifies that the circuit contains a qubit register q[n]
     and a classical register c[n].
  2) Runs the circuit on the AerSimulator backend for 'shots' times.
  3) Collects measurement outcomes as binary strings of length n.

Output:
  - A list of length 'shots' containing strings like "0101...", each of size n.
    Each string represents one random n-bit outcome from the quantum circuit.

Raises:
  - ValueError on invalid inputs or malformed circuits.
  - Exceptions from Qiskit parsing/simulation are propagated with context.
"""

def universal_execute(qasmstring: str, n: int):

    if not isinstance(n, int) or n < 1:
        raise ValueError("n must be a positive integer")

    circuit, msg = verify_qasm_syntax(qasmstring)
    if circuit is None:
        raise ValueError(f"QASM parsing failed: {msg}")


    q_regs = [qr for qr in circuit.qregs if qr.name == "q"]
    c_regs = [cr for cr in circuit.cregs if cr.name == "c"]
    if not q_regs or not c_regs:
        raise ValueError("QASM must define both 'q' and 'c' registers.")
    if len(q_regs[0]) < n or len(c_regs[0]) < n:
        raise ValueError("Register sizes do not match requested n.")


    aer_sim = AerSimulator()
    circ = transpile(circuit, aer_sim)
    result = aer_sim.run(circ, shots=1024).result()
    counts = result.get_counts()

    outcomes = []
    for bitstring, count in counts.items():
        outcomes.extend([bitstring] * count)

    return outcomes




if __name__ == "__main__":
    qasm_string = """
OPENQASM 3.0;
include "stdgates.inc";
bit[4] c;
qubit[4] q;
h q[0]; h q[1]; h q[2]; h q[3]; h q[4];
c[0] = measure q[0];
c[1] = measure q[1];
c[2] = measure q[2];
c[3] = measure q[3];
c[4] = measure q[4];

        """
    n = 5
    print('???')
    print(universal_check(qasm_string, n))


