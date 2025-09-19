from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.qasm3 import loads
import numpy as np
import traceback
def run_qasm_and_get_counts(qasm_code, shots=8192):
    circuit = loads(qasm_code)
    backend = AerSimulator()
    compiled = transpile(circuit, backend)
    result = backend.run(compiled, shots=shots).result()
    counts = result.get_counts()
    return counts
def verify_qasm_syntax(qasm_code):
    try:
        return loads(qasm_code),'syntax correct'
    except Exception as e:
        print("QASM parsing failed:", e)
        return None,str(f'"QASM parsing failed. {e}')
def theoretical_qft_probabilities(n):
    vec = np.zeros(2 ** n, dtype=complex)
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

def universal_check(qasm_code, n, shots=1024, threshold=0.01):
    try:
        circuit,report = verify_qasm_syntax(qasm_code)
        if circuit is None:
            return False, 0, report 
        measured_counts = run_qasm_and_get_counts(qasm_code, shots)
        theory_probs = theoretical_qft_probabilities(n)
        mse = compare_distributions(theory_probs, measured_counts, shots)
        success = mse < threshold
        success_rate = max(0.0, 1.0 - mse) 
        report = f"""
Qubit count: {n}
Shots: {shots}
Mean Squared Error (MSE): {mse:.6f}
Success threshold: {threshold}
Result: {"passed all tests" if success else "FAIL"}
"""
        return success, success_rate, report
    except Exception as e:
        #print(type(e))
        return False, 0.0, f"Error during simulation: {e},{type(e)}"


qft_universal_execute_description = """
universal_execute(qasm_code, qubit_num, inputstatestring) -> str

Purpose:
  Modify the provided OpenQASM 3.0 code to encode a computational-basis
  input state (given as a bitstring), run the circuit, and return the most
  likely measured n-bit output string.

Inputs (plain Python values):
  - qasm_code: str
      OpenQASM 3.0 code
  - qubit_num: int
      Number of qubits n. 
  - inputstatestring: str
      Bitstring of length n (e.g., "00010" or "100100").

Output:
  - The most frequent n-bit measurement string (e.g., "01011").

Raises:
  - ValueError on invalid inputs or qubit/register mismatches.
  - Underlying Qiskit parsing/simulation errors with context.
"""

def universal_execute(qasm_code: str, qubit_num: int, inputstatestring: str):
    from qiskit import QuantumCircuit, ClassicalRegister, transpile
    from qiskit.qasm3 import loads, dumps
    from qiskit_aer import AerSimulator
    n = qubit_num
    if not isinstance(n, int) or n < 1:
        raise ValueError("qubit_num must be a positive integer")
    if not isinstance(inputstatestring, str) or len(inputstatestring) != n or any(ch not in "01" for ch in inputstatestring):
        raise ValueError(f"inputstatestring must be a length-{n} bitstring of '0'/'1'")
    try:
        dut = loads(qasm_code)
    except Exception as e:
        raise ValueError(f"QASM parsing failed: {e}")

    if dut.num_qubits != n:
        raise ValueError(f"Qubit count mismatch: expected {n}, got {dut.num_qubits}")
    qreg = None
    for qr in dut.qregs:
        if qr.name == "q":
            qreg = qr
            break
    if qreg is None:
        if len(dut.qregs) != 1:
            raise ValueError("Cannot determine which qubits to prepare; please name the main register 'q'.")
        qreg = dut.qregs[0]
    if len(qreg) < n:
        raise ValueError(f"Register '{qreg.name}' is smaller than n={n}.")

    wrapper = QuantumCircuit(*dut.qregs, *dut.cregs)
    for i in range(n):
        if inputstatestring[-1 - i] == "1":
            wrapper.x(qreg[i])

    wrapper.compose(dut, inplace=True)
    dut_has_measure = any(inst.operation.name == "measure" for inst in dut.data)
    if not dut_has_measure:

        total_cbits = sum(len(cr) for cr in wrapper.cregs)
        if total_cbits < n:
            wrapper.add_register(ClassicalRegister(n - total_cbits, f"c{len(wrapper.cregs)}"))
        wrapper.barrier(qreg)
        wrapper.measure(qreg[:n], list(range(n)))

    modified_qasm = dumps(wrapper) 
    sim_circ = loads(modified_qasm)

    sim = AerSimulator()
    compiled = transpile(sim_circ, sim)
    result = sim.run(compiled, shots=4096).result()
    counts = result.get_counts(compiled)

    winner_state = max(counts, key=counts.get)
    return winner_state


if __name__ == "__main__":
    qasm_code = '''OPENQASM 3.0;
include "stdgates.inc";
bit[5] c;
qubit[5] q;
U(pi, 0, pi) q[0];
U(pi/2, 0, pi) q[4];
U(0, 0, pi/4) q[4];
cx q[4], q[3];
U(0, 0, -pi/4) q[3];
cx q[4], q[3];
U(0, 0, pi/4) q[3];
U(pi/2, 0, pi) q[3];
U(0, 0, pi/4) q[3];
U(0, 0, pi/8) q[4];
cx q[4], q[2];
U(0, 0, -pi/8) q[2];
cx q[4], q[2];
U(0, 0, pi/8) q[2];
cx q[3], q[2];
U(0, 0, -pi/4) q[2];
cx q[3], q[2];
U(0, 0, pi/4) q[2];
U(pi/2, 0, pi) q[2];
U(0, 0, pi/4) q[2];
U(0, 0, pi/8) q[3];
U(0, 0, pi/16) q[4];
cx q[4], q[1];
U(0, 0, -pi/16) q[1];
cx q[4], q[1];
U(0, 0, pi/16) q[1];
cx q[3], q[1];
U(0, 0, -pi/8) q[1];
cx q[3], q[1];
U(0, 0, pi/8) q[1];
cx q[2], q[1];
U(0, 0, -pi/4) q[1];
cx q[2], q[1];
U(0, 0, pi/4) q[1];
U(pi/2, 0, pi) q[1];
U(0, 0, pi/4) q[1];
U(0, 0, pi/8) q[2];
U(0, 0, pi/16) q[3];
U(0, 0, pi/32) q[4];
cx q[4], q[0];
U(0, 0, -pi/32) q[0];
cx q[4], q[0];
U(0, 0, pi/32) q[0];
cx q[3], q[0];
U(0, 0, -pi/16) q[0];
cx q[3], q[0];
U(0, 0, pi/16) q[0];
cx q[2], q[0];
U(0, 0, -pi/8) q[0];
cx q[2], q[0];
U(0, 0, pi/8) q[0];
cx q[1], q[0];
U(0, 0, -pi/4) q[0];
cx q[1], q[0];
U(0, 0, pi/4) q[0];
U(pi/2, 0, pi) q[0];
c[0] = measure q[0];
c[1] = measure q[1];
c[2] = measure q[2];
c[3] = measure q[3];
c[4] = measure q[4];
'''
    rep=universal_execute(qasm_code, 5, '01100')
    print(rep)
