

from typing import Tuple, Optional, List

from qiskit import QuantumCircuit, QuantumRegister, transpile
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector, state_fidelity
from qiskit.qasm3 import loads as qasm3_loads




def _find_qreg(qc: QuantumCircuit, name: str) -> QuantumRegister:
    for qreg in qc.qregs:
        if qreg.name == name:
            return qreg
    raise ValueError(f"Quantum register '{name}' not found in circuit.")


def verify_qasm_syntax(qasm_code):
    try:
        return qasm3_loads(qasm_code),'syntax correct'
    except Exception as e:
        print("QASM parsing failed:", e)
        return None,str(f'"QASM parsing failed. {e}')


def make_reference_cluster_qc(n: int) -> QuantumCircuit:
    q = QuantumRegister(n, "q")
    qc = QuantumCircuit(q)
    for i in range(n):
        qc.h(q[i])
    for i in range(n - 1):
        qc.cz(q[i], q[i + 1])
    return qc


def get_statevector_robust(qc: QuantumCircuit) -> Statevector:


    try:
        return Statevector.from_instruction(qc)
    except Exception:
        pass 


    sim = AerSimulator(method="statevector")
    qc2 = qc.copy()
    qc2.save_statevector()
    tqc = transpile(qc2, sim)
    result = sim.run(tqc).result()
    return result.data(0)["statevector"]



def universal_check(
    qasm_string: str,
    n: int,
    *,
    tol: float = 1e-6,
) -> Tuple[bool, float, str]:

    report: List[str] = []

    # 1) Syntax
    base_qc, msg = verify_qasm_syntax(qasm_string)
    report.append(f"Syntax: {msg}")
    if base_qc is None:
        return False, 0.0, "\n".join(report)

    # 2) Register check
    try:
        q_qr = _find_qreg(base_qc, "q")
    except Exception as e:
        report.append(f"Register check failed: {e}")
        return False, 0.0, "\n".join(report)

    if len(q_qr) < n:
        report.append(f"Register size mismatch: expected {n} qubits in 'q', found {len(q_qr)}.")
        return False, 0.0, "\n".join(report)

    try:
        dut_state = get_statevector_robust(base_qc)
    except Exception as e:
        report.append(f"Simulation failed: {e}")
        return False, 0.0, "\n".join(report)


    ref_qc = make_reference_cluster_qc(n)
    ref_state = Statevector.from_instruction(ref_qc)

    # 5) Fidelity
    fid = state_fidelity(dut_state, ref_state)
    ok = abs(fid - 1.0) < tol
    report.append(f"Fidelity with ideal cluster state = {fid:.6f}")
    report.append("passed all tests" if ok else "failed, not accurate")
    if ok:
        return True, fid, "\n".join(report)
    else:
        return False, fid, "\n".join(report)



cluster_universal_execute_description = """
universal_execute(qasm_code, n) -> str

Purpose:
  Execute an n-qubit Cluster  state circuit given in OpenQASM 3.0,
  measure all n qubits, and return the most probable measurement outcome.

Inputs:
  - qasm_code: str
      OpenQASM 3.0 program that prepares an n-qubit cluster state.
      Must define a quantum register 'q' with at least n qubits.
  - n: int
      Number of qubits to evaluate. Must be >= 1 and not exceed the size of 'q'.

Behavior:
  1) Parse qasm_code and verify 'q' has at least n qubits.
  2) Ensure there is a classical register and measurements for all n qubits.
  3) Simulate with AerSimulator for 1024 shots.
  4) Return the most frequent bitstring (Qiskit MSB-left convention).

Output:
  - winner_state: str
      The n-bit measurement string with the highest observed count.

Errors:
  - ValueError on invalid inputs or register mismatches.
  - Propagates Qiskit parsing/simulation exceptions with context.
"""

def universal_execute(qasm_code: str, n: int) -> str:
    from qiskit import QuantumCircuit, ClassicalRegister, transpile
    from qiskit_aer import AerSimulator


    base_qc, msg = verify_qasm_syntax(qasm_code)
    if base_qc is None:
        raise ValueError(f"QASM parsing failed: {msg}")

    q_qr = _find_qreg(base_qc, "q")
    if len(q_qr) < n:
        raise ValueError(f"Register 'q' has {len(q_qr)} qubits; expected at least {n}.")

    # Ensure measurements exist for the first n qubits
    has_measure = any(inst.operation.name == "measure" for inst in base_qc.data)
    if not has_measure:
        # Make sure we have at least n classical bits
        total_cbits = sum(len(cr) for cr in base_qc.cregs)
        if total_cbits < n:
            base_qc.add_register(ClassicalRegister(n - total_cbits, f"c{len(base_qc.cregs)}"))
        # Measure q[0..n-1] into classical bits 0..n-1
        base_qc.barrier(q_qr[:n])
        base_qc.measure(range(n), range(n))

    # Simulate with fixed 1024 shots
    sim = AerSimulator()
    tqc = transpile(base_qc, sim)
    result = sim.run(tqc, shots=1024).result()
    counts = result.get_counts(tqc)

    # Return the most probable outcome (MSB-left string)
    winner_state = max(counts.items(), key=lambda kv: kv[1])[0]
    return winner_state




if __name__ == "__main__":
    qasm_string = '''
OPENQASM 3.0;
include "stdgates.inc";
qubit[6] q;
h q[0];
h q[1];
h q[2];
h q[3];
h q[4];
h q[5];
cz q[0], q[1];
cz q[1], q[2];
cz q[2], q[3];
cz q[3], q[4];
cz q[4], q[5];
'''
    ok, fid, report = universal_check(qasm_string, n=6)
    print(ok, fid)
    print(report)
