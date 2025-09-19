

from typing import Tuple, Optional, List

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator
from qiskit.qasm3 import loads as qasm3_loads



def _find_qreg(qc: QuantumCircuit, name: str) -> QuantumRegister:
    for qreg in qc.qregs:
        if qreg.name == name:
            return qreg
    raise ValueError(f"Quantum register '{name}' not found in circuit.")


def _x_prep_bits(qc: QuantumCircuit, qreg: QuantumRegister, value: int, n: int) -> None:
    for i in range(n):
        if (value >> i) & 1:
            qc.x(qreg[i])


def _append_measure_all(qc: QuantumCircuit, qreg: QuantumRegister) -> ClassicalRegister:

    n = len(qreg)
    creg = ClassicalRegister(n, "res")
    qc.add_register(creg)
    for i in range(n):
        qc.measure(qreg[i], creg[i])
    return creg


def _counts_key_to_int_and_str(bitstring: str, n: int) -> Tuple[int, str]:

    rev = bitstring
    intval = int(rev, 2)
    return intval, rev



def verify_qasm_syntax(qasm_string: str) -> Tuple[Optional[QuantumCircuit], str]:
    try:
        qc = qasm3_loads(qasm_string)
        return qc, "syntax correct"
    except Exception as e:
        return None, f"QASM parsing failed. {e}"


def _simulate_winner_bitstring(qc: QuantumCircuit, shots: int) -> str:
    sim = AerSimulator()
    tqc = transpile(
        qc,
        backend=sim,
        optimization_level=0,     
        layout_method="trivial", 
        routing_method="none",   
    )
    result = sim.run(tqc, shots=shots).result()
    counts = result.get_counts()
    return max(counts.items(), key=lambda kv: kv[1])[0]


def _rotr1(value: int, n: int) -> int:
    mask = (1 << n) - 1
    return ((value >> 1) | ((value & 1) << (n - 1))) & mask


def _fmt_bits(x: int, n: int) -> str:
    return f"{x:0{n}b}"




def universal_check(
    qasm_string: str,
    n: int,
    *,
    shots: int = 1000,
) -> Tuple[bool, float, str]:
    report: List[str] = []


    base_qc, msg = verify_qasm_syntax(qasm_string)
    report.append(f"Syntax: {msg}")
    if base_qc is None:
        return False, 0.0, "\n".join(report)


    try:
        q_qr = _find_qreg(base_qc, "q")
    except Exception as e:
        report.append(f"Register check failed: {e}")
        return False, 0.0, "\n".join(report)

    if len(q_qr) < n:
        report.append(f"Register size mismatch: expected {n}, found {len(q_qr)}")
        return False, 0.0, "\n".join(report)

    mask_all = (1 << n) - 1
    alt_01 = int("01" * ((n + 1) // 2), 2) & mask_all
    alt_10 = int("10" * ((n + 1) // 2), 2) & mask_all


    fixed_cases = [
        0,              
        1 << (n - 2),  
        1 << 1,        
    ]

    passes = 0
    for t, in_val in enumerate(fixed_cases, start=1):
        try:
            test_qc = QuantumCircuit(*base_qc.qregs)
            _x_prep_bits(test_qc, q_qr, in_val, n)
            test_qc.compose(base_qc, inplace=True)
            test_qc.barrier(q_qr)
            _append_measure_all(test_qc, q_qr)

            winner = _simulate_winner_bitstring(test_qc, shots)
            out_int, out_str = _counts_key_to_int_and_str(winner, n)
            exp_out = _rotr1(in_val, n)
            exp_str = _fmt_bits(exp_out, n)
            ok = (out_int == exp_out)
            if ok:
                passes += 1

            report.append(
                f"Trial {t}: [in={_fmt_bits(in_val, n)}]  "
                f"meas(q={out_str})  "
                f"exp(q={exp_str})  "
                f"{'PASS' if ok else 'FAIL'}"
            )
        except Exception as e:
            report.append(f"Trial {t}: ERROR: {e}")

    score = passes / len(fixed_cases)
    report.append(f"Summary: {passes}/{len(fixed_cases)} passed  |  score={score:.2f}  |  shots={shots}")
    overall = "Passed all tests" if passes == len(fixed_cases) else ("Functional check PARTIAL" if passes > 0 else "Functional check FAILED")
    if passes==len(fixed_cases):
        return True, score, f"{overall}\n" + "\n".join(report)
    else:
        return False, score, f"{overall}\n" + "\n".join(report)


universal_execute_description = """
universal_execute(qasm_string, n, input_str) -> str

Purpose:
  Execute a QASM circuit that implements a 1-position cyclic permutation
  (left-rotate by 1) over a single quantum register q[n], on a concrete
  n-bit string input, and return the measured output.

Inputs:
  - qasm_string: str
      OpenQASM 3.0 source. 
  - n: int
      number of qubits used).
  - input_str: str
      String of '0'/'1' of length n (e.g., "01101"). 

Behavior:
  1) Parses qasm_string and verifies register q of size at least n.
  2) Prepares q by applying X to qubits corresponding to '1' bits of input_str.
  3) Composes the DUT circuit, measures all q[i] into classical bits, and
     runs the circuit on AerSimulator for 'shots' shots.
  4) Picks the most frequent outcome and returns it as a bitstring.

Output:
  - out_str: the winning measurement bitstring (MSB-left as returned by Qiskit).

Errors:
  - ValueError for invalid inputs or register mismatch.
  - Qiskit parsing/simulation exceptions are propagated with context.
"""

def universal_execute(qasm_string: str, n: int, input_str: str) -> str:

    if not isinstance(n, int) or n < 1:
        raise ValueError("n must be a positive integer")
    if not isinstance(input_str, str) or len(input_str) != n or any(ch not in "01" for ch in input_str):
        raise ValueError(f"input_str must be a bitstring of length {n}")

    base_qc, msg = verify_qasm_syntax(qasm_string)
    if base_qc is None:
        raise ValueError(f"QASM parsing failed: {msg}")

    q_qr = _find_qreg(base_qc, "q")
    if len(q_qr) < n:
        raise ValueError(f"Register 'q' size mismatch: expected at least {n}, found {len(q_qr)}")


    from qiskit import QuantumCircuit
    wrapper = QuantumCircuit(*base_qc.qregs)
    for i in range(n):
        if input_str[-1 - i] == "1": 
            wrapper.x(q_qr[i])
    wrapper.compose(base_qc, inplace=True)
    wrapper.barrier(q_qr)
    _append_measure_all(wrapper, q_qr)

    winner = _simulate_winner_bitstring(wrapper, 1024)
    _, out_str = _counts_key_to_int_and_str(winner, n)
    return out_str




if __name__ == "__main__":
    qasm_string = '''
OPENQASM 3.0;
include "stdgates.inc";
gate permutation__1_2_3_4_5_6_0_ _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3, _gate_q_4, _gate_q_5, _gate_q_6 {
  swap _gate_q_5, _gate_q_6;
  swap _gate_q_4, _gate_q_6;
  swap _gate_q_3, _gate_q_6;
  swap _gate_q_2, _gate_q_6;
  swap _gate_q_1, _gate_q_6;
  swap _gate_q_0, _gate_q_6;
}
qubit[7] q;
permutation__1_2_3_4_5_6_0_ q[0], q[1], q[2], q[3], q[4], q[5], q[6];
'''
    ok, score, report = universal_check(qasm_string, n=7)
    print(ok, score)
    print(report)
