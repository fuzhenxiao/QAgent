import random
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


def _append_measure_b_and_cout(qc: QuantumCircuit, b_qr: QuantumRegister, cout_qr: QuantumRegister, n: int) -> ClassicalRegister:

    creg = ClassicalRegister(n + 1, "res")
    qc.add_register(creg)
    for i in range(n):           # sum bits
        qc.measure(b_qr[i], creg[i])
    qc.measure(cout_qr[0], creg[n])
    return creg


def _decode_sum_and_cout_from_counts_key(bitstring: str, n: int) -> Tuple[int, int]:

    if len(bitstring) < n + 1:
        raise ValueError("Counts key is shorter than expected.")
    cout = int(bitstring[0])  # leftmost is cout
    s = 0
    for i in range(n):
        s |= int(bitstring[-(i + 1)]) << i  
    return s, cout


def _expected_sum(a_val: int, b_val: int, cin_bit: int, n: int) -> Tuple[int, int]:
    total = a_val + b_val + cin_bit
    return total & ((1 << n) - 1), (total >> n) & 1


def _simulate_and_decode(qc: QuantumCircuit, n: int, shots: int) -> Tuple[int, int]:
    sim = AerSimulator()
    tqc = transpile(qc, sim)
    result = sim.run(tqc, shots=shots).result()
    counts = result.get_counts()
    winner = max(counts.items(), key=lambda kv: kv[1])[0]
    return _decode_sum_and_cout_from_counts_key(winner, n)




def verify_qasm_syntax(qasm_string: str) -> Tuple[Optional[QuantumCircuit], str]:

    try:
        qc = qasm3_loads(qasm_string)
        return qc, "syntax correct"
    except Exception as e:
        return None, f"QASM parsing failed. {e}"


def universal_check(
    qasm_string: str,
    n: int,
    *,
    shots: int = 1000,
) -> Tuple[bool, float, str]:

    report: List[str] = []

    # 1) syntax
    base_qc, msg = verify_qasm_syntax(qasm_string)
    report.append(f"Syntax: {msg}")
    if base_qc is None:
        return False, 0.0, "\n".join(report)

    # 2) locate regs
    try:
        a_qr = _find_qreg(base_qc, "a")
        b_qr = _find_qreg(base_qc, "b")
        cin_qr = _find_qreg(base_qc, "cin")
        cout_qr = _find_qreg(base_qc, "cout")
    except Exception as e:
        report.append(f"Register check failed: {e}")
        return False, 0.0, "\n".join(report)

    if len(a_qr) < n or len(b_qr) < n or len(cin_qr) < 1 or len(cout_qr) < 1:
        report.append("Register sizes do not match n or cin/cout missing.")
        return False, 0.0, "\n".join(report)


    fixed_cases = [
        (0, 1, 0),                    # trial 1
        (1 << (n - 1), 0, 0),         # trial 2
        ((1 << n) - 1, (1 << n) - 1, 1),  # trial 3
    ]

    passes = 0
    for t, (a_val, b_val, cin_bit) in enumerate(fixed_cases, start=1):
        try:

            test_qc = QuantumCircuit(*base_qc.qregs)


            _x_prep_bits(test_qc, a_qr, a_val, n)
            _x_prep_bits(test_qc, b_qr, b_val, n)
            if cin_bit == 1:
                test_qc.x(cin_qr[0])

            test_qc.compose(base_qc, inplace=True)


            _append_measure_b_and_cout(test_qc, b_qr, cout_qr, n)


            sum_meas, cout_meas = _simulate_and_decode(test_qc, n, shots)
            exp_sum, exp_cout = _expected_sum(a_val, b_val, cin_bit, n)
            ok = (sum_meas == exp_sum) and (cout_meas == exp_cout)
            if ok:
                passes += 1

            report.append(
                f"Trial {t}: [a={a_val:0{n}b} b={b_val:0{n}b} cin={cin_bit}]  "
                f"meas(sum={sum_meas:0{n}b}, cout={cout_meas})  "
                f"exp(sum={exp_sum:0{n}b}, cout={exp_cout})  "
                f"{'PASS' if ok else 'FAIL'}"
            )
        except Exception as e:
            report.append(f"Trial {t}: ERROR: {e}")

    score = passes / 3.0
    report.append(f"Summary: {passes}/3 passed  |  score={score:.2f}  |  shots={shots}")
    overall = "passed all tests" if passes == 3 else ("partially correct" if passes > 0 else "Functional check FAILED")
    if passes==3:
        return True, score, f"{overall}\n" 
    else:
        return False, score, f"{overall}\n" 


universal_execute_description = """
universal_execute(qasmstring: str, n: int, inputa: str, inputb: str, cin: str) -> (sum_str: str, cout_str: str)

Purpose:
  Execute an n-bit adder circuit (OpenQASM 3.0) with fixed registers a[n], b[n], cin[1], cout[1],
  where the SUM is written into register 'b' (Cuccaro-style). Inputs and outputs are bitstrings.

Inputs (plain Python strings, NOT integers or quantum registers):
  - qasmstring: str
      OpenQASM 3.0 source that declares: a[n], b[n], cin[1], cout[1].
  - n: int
      Bit width (n >= 1).
  - inputa: str
      Bitstring of length n for register a, e.g. "0101".
      Mapping uses LSB-right: inputa[-1] -> a[0], inputa[-2] -> a[1], ... inputa[0] -> a[n-1].
  - inputb: str
      Bitstring of length n for register b (same mapping as above).
  - cin: str
      Single-bit string "0" or "1" for cin[0].

Behavior:
  1) Parses qasmstring and checks presence/sizes of a[n], b[n], cin[1], cout[1].
  2) Builds a wrapper that prepares a and b from the input bitstrings (X on '1' bits) and sets cin if "1".
  3) Composes the DUT, measures SUM (b[0..n-1]) and cout[0] into a fresh classical register.
  4) Simulates with AerSimulator for exactly 1024 shots and returns the most frequent outcome.

Output:
  - (sum_str, cout_str):
      * sum_str: n-bit string for the measured sum in MSB-left order as reported by Qiskit.
                 (This equals the rightmost n characters of the winning counts key.)
      * cout_str: "0" or "1" (the leftmost character of the winning counts key).

Errors:
  - ValueError for invalid inputs or missing/mismatched registers.
  - Qiskit parsing/simulation exceptions are propagated with context.
"""

def universal_execute(
    qasmstring: str,
    n: int,
    inputa: str,
    inputb: str,
    cin: str,
) -> (str, str):

    if not isinstance(n, int) or n < 1:
        raise ValueError("n must be a positive integer")
    for name, s in (("inputa", inputa), ("inputb", inputb)):
        if not isinstance(s, str) or len(s) != n or any(ch not in "01" for ch in s):
            raise ValueError(f"{name} must be a bitstring of length {n}")
    if cin not in ("0", "1"):
        raise ValueError("cin must be '0' or '1'")

    base_qc, msg = verify_qasm_syntax(qasmstring)
    if base_qc is None:
        raise ValueError(f"QASM parsing failed: {msg}")

    a_qr = _find_qreg(base_qc, "a")
    b_qr = _find_qreg(base_qc, "b")
    cin_qr = _find_qreg(base_qc, "cin")
    cout_qr = _find_qreg(base_qc, "cout")

    if len(a_qr) < n or len(b_qr) < n or len(cin_qr) < 1 or len(cout_qr) < 1:
        raise ValueError("Register sizes do not match n or cin/cout missing.")


    from qiskit import QuantumCircuit
    wrapper = QuantumCircuit(*base_qc.qregs)

    for i in range(n):
        if inputa[-1 - i] == "1":
            wrapper.x(a_qr[i])
        if inputb[-1 - i] == "1":
            wrapper.x(b_qr[i])
    if cin == "1":
        wrapper.x(cin_qr[0])


    wrapper.compose(base_qc, inplace=True)
    _append_measure_b_and_cout(wrapper, b_qr, cout_qr, n)


    sim = AerSimulator()
    tqc = transpile(wrapper, sim)
    result = sim.run(tqc, shots=1024).result()
    counts = result.get_counts()

    winner = max(counts.items(), key=lambda kv: kv[1])[0]  
    cout_str = winner[0]
    sum_str = winner[-n:] 

    return sum_str, cout_str


if __name__ == "__main__":
    qasm_string = '''
OPENQASM 3.0;
include "stdgates.inc";
gate MAJ _gate_q_0, _gate_q_1, _gate_q_2 {
  cx _gate_q_0, _gate_q_1;
  cx _gate_q_0, _gate_q_2;
  ccx _gate_q_2, _gate_q_1, _gate_q_0;
}
gate UMA _gate_q_0, _gate_q_1, _gate_q_2 {
  ccx _gate_q_2, _gate_q_1, _gate_q_0;
  cx _gate_q_0, _gate_q_2;
  cx _gate_q_2, _gate_q_1;
}
gate FullAdder _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3, _gate_q_4, _gate_q_5, _gate_q_6, _gate_q_7, _gate_q_8, _gate_q_9, _gate_q_10, _gate_q_11 {
  MAJ _gate_q_1, _gate_q_6, _gate_q_0;
  MAJ _gate_q_2, _gate_q_7, _gate_q_1;
  MAJ _gate_q_3, _gate_q_8, _gate_q_2;
  MAJ _gate_q_4, _gate_q_9, _gate_q_3;
  MAJ _gate_q_5, _gate_q_10, _gate_q_4;
  cx _gate_q_5, _gate_q_11;
  UMA _gate_q_5, _gate_q_10, _gate_q_4;
  UMA _gate_q_4, _gate_q_9, _gate_q_3;
  UMA _gate_q_3, _gate_q_8, _gate_q_2;
  UMA _gate_q_2, _gate_q_7, _gate_q_1;
  UMA _gate_q_1, _gate_q_6, _gate_q_0;
}
qubit[5] a;
qubit[5] b;
qubit[1] cin;
qubit[1] cout;
FullAdder a[0], a[1], a[2], a[3], a[4], b[0], b[1], b[2], b[3], b[4], cin[0], cout[0];
'''
    ok, score, report = universal_check(qasm_string, n=5)
    print(ok, score)
    print(report)
