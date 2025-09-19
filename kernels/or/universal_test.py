#!/usr/bin/env python3
"""
Universal checker for your fixed-format OR QASM (OpenQASM 3.0).

Assumptions (fixed by your format):
  - Registers: in[n], out[1]
  - Logical OR of all bits in 'in' should be written to out[0]

Default: shots=1000. Uses several fixed trials derived from n.
"""

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


def _append_measure_out(qc: QuantumCircuit, out_qr: QuantumRegister) -> ClassicalRegister:

    creg = ClassicalRegister(1, "res")
    qc.add_register(creg)
    qc.measure(out_qr[0], creg[0])
    return creg


def _decode_out_from_counts_key(bitstring: str) -> int:

    if len(bitstring) < 1:
        raise ValueError("Counts key is shorter than expected.")
    return int(bitstring[-1])  


def _expected_or(in_val: int) -> int:

    return 1 if in_val != 0 else 0


def verify_qasm_syntax(qasm_string: str) -> Tuple[Optional[QuantumCircuit], str]:

    try:
        qc = qasm3_loads(qasm_string)
        return qc, "syntax correct"
    except Exception as e:
        return None, f"QASM parsing failed. {e}"


def _simulate_and_decode(qc: QuantumCircuit, shots: int) -> int:
    sim = AerSimulator()
    tqc = transpile(qc, sim)
    result = sim.run(tqc, shots=shots).result()
    counts = result.get_counts()

    winner = max(counts.items(), key=lambda kv: kv[1])[0]
    return _decode_out_from_counts_key(winner)


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
        in_qr = _find_qreg(base_qc, "in_0")
        out_qr = _find_qreg(base_qc, "out")
    except Exception as e:
        report.append(f"Register check failed: {e}")
        return False, 0.0, "\n".join(report)

    if len(in_qr) < n or len(out_qr) < 1:
        report.append("Register sizes do not match n or 'out' missing.")
        return False, 0.0, "\n".join(report)

    # 3) fixed trials
    all_ones = (1 << n) - 1
    alternating_lsb1 = int("01" * ((n + 1) // 2), 2) & all_ones  # 0101... up to n bits

    fixed_cases = [
        0,                        # all zeros
        1,                        # only LSB set
        (1 << (n - 1)),           # only MSB set
        alternating_lsb1,         # 0101...
        all_ones,                 # all ones
    ]

    passes = 0
    for t, in_val in enumerate(fixed_cases, start=1):
        try:

            test_qc = QuantumCircuit(*base_qc.qregs)

            _x_prep_bits(test_qc, in_qr, in_val, n)

            test_qc.compose(base_qc, inplace=True)

            _append_measure_out(test_qc, out_qr)

            out_meas = _simulate_and_decode(test_qc, shots)
            exp_out = _expected_or(in_val)
            ok = (out_meas == exp_out)
            if ok:
                passes += 1

            report.append(
                f"Trial {t}: [in={in_val:0{n}b}]  "
                f"meas(out={out_meas})  "
                f"exp(out={exp_out})  "
                f"{'PASS' if ok else 'FAIL'}"
            )
        except Exception as e:
            report.append(f"Trial {t}: ERROR: {e}")

    score = passes / len(fixed_cases)
    report.append(f"Summary: {passes}/{len(fixed_cases)} passed  |  score={score:.2f}  |  shots={shots}")
    overall = "passed all tests" if passes == len(fixed_cases) else ("Functional check PARTIAL" if passes > 0 else "Functional check FAILED")
    if passes == len(fixed_cases):
        return True, score, f"{overall}\n" + "\n".join(report)
    else:
        return False, score, f"{overall}\n" + "\n".join(report)
# ---------------- OR execution API ----------------

or_universal_execute_description = """
universal_execute(qasm_string: str, input_str: str) -> str

Purpose:
  Execute a fixed-format OR circuit in OpenQASM 3.0 with registers:
    in_0[n], out[1]
  Prepare the computational-basis input from 'input_str', run the circuit,
  and return the most probable measured value of out[0] as a string.

Inputs:
  - qasm_string: str
      OpenQASM 3.0 source that declares qubit[n] in_0; qubit[1] out; and
      writes the logical OR(in_0[0..n-1]) into out[0].
  - input_str: str
      Bitstring like "010011". Its length n determines how many input qubits
      are prepared. Mapping uses LSB-right:
        input_str[-1] -> in_0[0]
        input_str[-2] -> in_0[1]
        ...
        input_str[0]  -> in_0[n-1]

Behavior:
  1) Parses qasm_string; verifies presence/sizes of in_0[n] and out[1].
  2) Builds a wrapper that applies X to in_0[i] for each '1' in input_str and
     composes the DUT.
  3) Measures out[0] into a fresh classical bit.
  4) Simulates with AerSimulator for exactly 1024 shots.
  5) Returns the winning measurement for out (\"0\" or \"1\") as a string.

Output:
  - winner_out: str
      \"0\" or \"1\", the most frequent measurement of out[0].

Errors:
  - ValueError for invalid inputs, missing registers, or size mismatches.
  - Qiskit parsing/simulation exceptions are propagated with context.
"""

def universal_execute(qasm_string: str, input_str: str) -> str:
    from qiskit import QuantumCircuit

    if not isinstance(input_str, str) or len(input_str) == 0 or any(ch not in "01" for ch in input_str):
        raise ValueError("input_str must be a non-empty bitstring of '0'/'1'")
    n = len(input_str)

    base_qc, msg = verify_qasm_syntax(qasm_string)
    if base_qc is None:
        raise ValueError(f"QASM parsing failed: {msg}")

    in_qr = _find_qreg(base_qc, "in_0")
    out_qr = _find_qreg(base_qc, "out")
    if len(in_qr) < n or len(out_qr) < 1:
        raise ValueError(f"Register sizes mismatch: in_0 has {len(in_qr)} qubits, out has {len(out_qr)} (need >= {n} and >= 1).")

    wrapper = QuantumCircuit(*base_qc.qregs)
    in_val = int(input_str, 2) 
    _x_prep_bits(wrapper, in_qr, in_val, n) 

    wrapper.compose(base_qc, inplace=True)
    _append_measure_out(wrapper, out_qr)

    out_bit = _simulate_and_decode(wrapper, shots=1024)
    return "1" if out_bit == 1 else "0"


if __name__ == "__main__":
    qasm_string = '''
OPENQASM 3.0;
include "stdgates.inc";
gate mcx_vchain_dg _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3, _gate_q_4 {
  h _gate_q_3;
  cx _gate_q_0, _gate_q_3;
  p(pi/8) _gate_q_3;
  cx _gate_q_2, _gate_q_3;
  p(-pi/8) _gate_q_3;
  cx _gate_q_1, _gate_q_3;
  p(pi/8) _gate_q_3;
  cx _gate_q_2, _gate_q_3;
  p(-pi/8) _gate_q_3;
  cx _gate_q_0, _gate_q_3;
  p(pi/8) _gate_q_3;
  cx _gate_q_2, _gate_q_3;
  p(-pi/8) _gate_q_3;
  cx _gate_q_1, _gate_q_3;
  p(pi/8) _gate_q_3;
  cx _gate_q_2, _gate_q_3;
  cx _gate_q_0, _gate_q_2;
  p(pi/8) _gate_q_2;
  cx _gate_q_1, _gate_q_2;
  p(-pi/8) _gate_q_2;
  cx _gate_q_0, _gate_q_2;
  p(pi/8) _gate_q_2;
  cx _gate_q_1, _gate_q_2;
  cx _gate_q_0, _gate_q_1;
  p(pi/8) _gate_q_1;
  cx _gate_q_0, _gate_q_1;
  p(-pi/8) _gate_q_3;
  p(-pi/8) _gate_q_2;
  p(-pi/8) _gate_q_1;
  p(-pi/8) _gate_q_0;
  h _gate_q_3;
}
gate mcx_vchain _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3, _gate_q_4, _gate_q_5, _gate_q_6 {
  ccx _gate_q_3, _gate_q_6, _gate_q_4;
  h _gate_q_6;
  t _gate_q_6;
  cx _gate_q_2, _gate_q_6;
  tdg _gate_q_6;
  cx _gate_q_5, _gate_q_6;
  h _gate_q_5;
  t _gate_q_5;
  cx _gate_q_0, _gate_q_5;
  tdg _gate_q_5;
  cx _gate_q_1, _gate_q_5;
  t _gate_q_5;
  cx _gate_q_0, _gate_q_5;
  tdg _gate_q_5;
  h _gate_q_5;
  cx _gate_q_5, _gate_q_6;
  t _gate_q_6;
  cx _gate_q_2, _gate_q_6;
  tdg _gate_q_6;
  h _gate_q_6;
  ccx _gate_q_3, _gate_q_6, _gate_q_4;
  h _gate_q_6;
  t _gate_q_6;
  cx _gate_q_2, _gate_q_6;
  tdg _gate_q_6;
  cx _gate_q_5, _gate_q_6;
  h _gate_q_5;
  t _gate_q_5;
  cx _gate_q_0, _gate_q_5;
  tdg _gate_q_5;
  cx _gate_q_1, _gate_q_5;
  t _gate_q_5;
  cx _gate_q_0, _gate_q_5;
  tdg _gate_q_5;
  h _gate_q_5;
  cx _gate_q_5, _gate_q_6;
  t _gate_q_6;
  cx _gate_q_2, _gate_q_6;
  tdg _gate_q_6;
  h _gate_q_6;
}
gate mcx_vchain_0 _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3, _gate_q_4 {
  h _gate_q_3;
  p(pi/8) _gate_q_0;
  p(pi/8) _gate_q_1;
  p(pi/8) _gate_q_2;
  p(pi/8) _gate_q_3;
  cx _gate_q_0, _gate_q_1;
  p(-pi/8) _gate_q_1;
  cx _gate_q_0, _gate_q_1;
  cx _gate_q_1, _gate_q_2;
  p(-pi/8) _gate_q_2;
  cx _gate_q_0, _gate_q_2;
  p(pi/8) _gate_q_2;
  cx _gate_q_1, _gate_q_2;
  p(-pi/8) _gate_q_2;
  cx _gate_q_0, _gate_q_2;
  cx _gate_q_2, _gate_q_3;
  p(-pi/8) _gate_q_3;
  cx _gate_q_1, _gate_q_3;
  p(pi/8) _gate_q_3;
  cx _gate_q_2, _gate_q_3;
  p(-pi/8) _gate_q_3;
  cx _gate_q_0, _gate_q_3;
  p(pi/8) _gate_q_3;
  cx _gate_q_2, _gate_q_3;
  p(-pi/8) _gate_q_3;
  cx _gate_q_1, _gate_q_3;
  p(pi/8) _gate_q_3;
  cx _gate_q_2, _gate_q_3;
  p(-pi/8) _gate_q_3;
  cx _gate_q_0, _gate_q_3;
  h _gate_q_3;
}
gate mcx_vchain_1 _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3, _gate_q_4 {
  h _gate_q_3;
  p(pi/8) _gate_q_0;
  p(pi/8) _gate_q_1;
  p(pi/8) _gate_q_2;
  p(pi/8) _gate_q_3;
  cx _gate_q_0, _gate_q_1;
  p(-pi/8) _gate_q_1;
  cx _gate_q_0, _gate_q_1;
  cx _gate_q_1, _gate_q_2;
  p(-pi/8) _gate_q_2;
  cx _gate_q_0, _gate_q_2;
  p(pi/8) _gate_q_2;
  cx _gate_q_1, _gate_q_2;
  p(-pi/8) _gate_q_2;
  cx _gate_q_0, _gate_q_2;
  cx _gate_q_2, _gate_q_3;
  p(-pi/8) _gate_q_3;
  cx _gate_q_1, _gate_q_3;
  p(pi/8) _gate_q_3;
  cx _gate_q_2, _gate_q_3;
  p(-pi/8) _gate_q_3;
  cx _gate_q_0, _gate_q_3;
  p(pi/8) _gate_q_3;
  cx _gate_q_2, _gate_q_3;
  p(-pi/8) _gate_q_3;
  cx _gate_q_1, _gate_q_3;
  p(pi/8) _gate_q_3;
  cx _gate_q_2, _gate_q_3;
  p(-pi/8) _gate_q_3;
  cx _gate_q_0, _gate_q_3;
  h _gate_q_3;
}
gate mcx_vchain_2 _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3, _gate_q_4 {
  h _gate_q_3;
  p(pi/8) _gate_q_0;
  p(pi/8) _gate_q_1;
  p(pi/8) _gate_q_2;
  p(pi/8) _gate_q_3;
  cx _gate_q_0, _gate_q_1;
  p(-pi/8) _gate_q_1;
  cx _gate_q_0, _gate_q_1;
  cx _gate_q_1, _gate_q_2;
  p(-pi/8) _gate_q_2;
  cx _gate_q_0, _gate_q_2;
  p(pi/8) _gate_q_2;
  cx _gate_q_1, _gate_q_2;
  p(-pi/8) _gate_q_2;
  cx _gate_q_0, _gate_q_2;
  cx _gate_q_2, _gate_q_3;
  p(-pi/8) _gate_q_3;
  cx _gate_q_1, _gate_q_3;
  p(pi/8) _gate_q_3;
  cx _gate_q_2, _gate_q_3;
  p(-pi/8) _gate_q_3;
  cx _gate_q_0, _gate_q_3;
  p(pi/8) _gate_q_3;
  cx _gate_q_2, _gate_q_3;
  p(-pi/8) _gate_q_3;
  cx _gate_q_1, _gate_q_3;
  p(pi/8) _gate_q_3;
  cx _gate_q_2, _gate_q_3;
  p(-pi/8) _gate_q_3;
  cx _gate_q_0, _gate_q_3;
  h _gate_q_3;
}
gate mcx_vchain_dg_3 _gate_q_0, _gate_q_1, _gate_q_2 {
  ccx _gate_q_0, _gate_q_1, _gate_q_2;
}
gate mcx_vchain_4 _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3, _gate_q_4 {
  h _gate_q_3;
  p(pi/8) _gate_q_0;
  p(pi/8) _gate_q_1;
  p(pi/8) _gate_q_2;
  p(pi/8) _gate_q_3;
  cx _gate_q_0, _gate_q_1;
  p(-pi/8) _gate_q_1;
  cx _gate_q_0, _gate_q_1;
  cx _gate_q_1, _gate_q_2;
  p(-pi/8) _gate_q_2;
  cx _gate_q_0, _gate_q_2;
  p(pi/8) _gate_q_2;
  cx _gate_q_1, _gate_q_2;
  p(-pi/8) _gate_q_2;
  cx _gate_q_0, _gate_q_2;
  cx _gate_q_2, _gate_q_3;
  p(-pi/8) _gate_q_3;
  cx _gate_q_1, _gate_q_3;
  p(pi/8) _gate_q_3;
  cx _gate_q_2, _gate_q_3;
  p(-pi/8) _gate_q_3;
  cx _gate_q_0, _gate_q_3;
  p(pi/8) _gate_q_3;
  cx _gate_q_2, _gate_q_3;
  p(-pi/8) _gate_q_3;
  cx _gate_q_1, _gate_q_3;
  p(pi/8) _gate_q_3;
  cx _gate_q_2, _gate_q_3;
  p(-pi/8) _gate_q_3;
  cx _gate_q_0, _gate_q_3;
  h _gate_q_3;
}
gate mcx_vchain_5 _gate_q_0, _gate_q_1, _gate_q_2 {
  ccx _gate_q_0, _gate_q_1, _gate_q_2;
}
gate mcx_vchain_dg_6 _gate_q_0, _gate_q_1, _gate_q_2 {
  ccx _gate_q_0, _gate_q_1, _gate_q_2;
}
gate mcx_vchain_7 _gate_q_0, _gate_q_1, _gate_q_2 {
  ccx _gate_q_0, _gate_q_1, _gate_q_2;
}
gate mcx_vchain_8 _gate_q_0, _gate_q_1, _gate_q_2 {
  ccx _gate_q_0, _gate_q_1, _gate_q_2;
}
gate mcx_vchain_dg_9 _gate_q_0, _gate_q_1 {
  cx _gate_q_0, _gate_q_1;
}
gate mcx_vchain_10 _gate_q_0, _gate_q_1, _gate_q_2 {
  ccx _gate_q_0, _gate_q_1, _gate_q_2;
}
gate mcx_vchain_11 _gate_q_0, _gate_q_1 {
  cx _gate_q_0, _gate_q_1;
}
gate mcx_vchain_dg_12 _gate_q_0, _gate_q_1 {
  cx _gate_q_0, _gate_q_1;
}
gate mcx_vchain_13 _gate_q_0, _gate_q_1 {
  cx _gate_q_0, _gate_q_1;
}
gate mcx_vchain_14 _gate_q_0, _gate_q_1 {
  cx _gate_q_0, _gate_q_1;
}
gate mcphase(_gate_p_0) _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3, _gate_q_4, _gate_q_5, _gate_q_6, _gate_q_7 {
  ccx _gate_q_3, _gate_q_5, _gate_q_7;
  h _gate_q_5;
  t _gate_q_5;
  cx _gate_q_2, _gate_q_5;
  tdg _gate_q_5;
  cx _gate_q_4, _gate_q_5;
  h _gate_q_4;
  t _gate_q_4;
  cx _gate_q_0, _gate_q_4;
  tdg _gate_q_4;
  cx _gate_q_1, _gate_q_4;
  t _gate_q_4;
  cx _gate_q_0, _gate_q_4;
  tdg _gate_q_4;
  h _gate_q_4;
  cx _gate_q_4, _gate_q_5;
  t _gate_q_5;
  cx _gate_q_2, _gate_q_5;
  tdg _gate_q_5;
  h _gate_q_5;
  ccx _gate_q_3, _gate_q_5, _gate_q_7;
  h _gate_q_5;
  t _gate_q_5;
  cx _gate_q_2, _gate_q_5;
  tdg _gate_q_5;
  cx _gate_q_4, _gate_q_5;
  h _gate_q_4;
  t _gate_q_4;
  cx _gate_q_0, _gate_q_4;
  tdg _gate_q_4;
  cx _gate_q_1, _gate_q_4;
  t _gate_q_4;
  cx _gate_q_0, _gate_q_4;
  tdg _gate_q_4;
  h _gate_q_4;
  cx _gate_q_4, _gate_q_5;
  t _gate_q_5;
  cx _gate_q_2, _gate_q_5;
  tdg _gate_q_5;
  h _gate_q_5;
  rz(-pi/4) _gate_q_7;
  mcx_vchain_dg _gate_q_4, _gate_q_5, _gate_q_6, _gate_q_7, _gate_q_3;
  rz(pi/4) _gate_q_7;
  mcx_vchain _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3, _gate_q_7, _gate_q_4, _gate_q_5;
  rz(-pi/4) _gate_q_7;
  mcx_vchain_0 _gate_q_4, _gate_q_5, _gate_q_6, _gate_q_7, _gate_q_3;
  rz(pi/4) _gate_q_7;
  h _gate_q_6;
  p(pi/8) _gate_q_0;
  p(pi/8) _gate_q_1;
  p(pi/8) _gate_q_2;
  p(pi/8) _gate_q_6;
  cx _gate_q_0, _gate_q_1;
  p(-pi/8) _gate_q_1;
  cx _gate_q_0, _gate_q_1;
  cx _gate_q_1, _gate_q_2;
  p(-pi/8) _gate_q_2;
  cx _gate_q_0, _gate_q_2;
  p(pi/8) _gate_q_2;
  cx _gate_q_1, _gate_q_2;
  p(-pi/8) _gate_q_2;
  cx _gate_q_0, _gate_q_2;
  cx _gate_q_2, _gate_q_6;
  p(-pi/8) _gate_q_6;
  cx _gate_q_1, _gate_q_6;
  p(pi/8) _gate_q_6;
  cx _gate_q_2, _gate_q_6;
  p(-pi/8) _gate_q_6;
  cx _gate_q_0, _gate_q_6;
  p(pi/8) _gate_q_6;
  cx _gate_q_2, _gate_q_6;
  p(-pi/8) _gate_q_6;
  cx _gate_q_1, _gate_q_6;
  p(pi/8) _gate_q_6;
  cx _gate_q_2, _gate_q_6;
  p(-pi/8) _gate_q_6;
  cx _gate_q_0, _gate_q_6;
  h _gate_q_6;
  rz(-pi/8) _gate_q_6;
  mcx_vchain_dg _gate_q_3, _gate_q_4, _gate_q_5, _gate_q_6, _gate_q_2;
  rz(pi/8) _gate_q_6;
  mcx_vchain_1 _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_6, _gate_q_3;
  rz(-pi/8) _gate_q_6;
  mcx_vchain_2 _gate_q_3, _gate_q_4, _gate_q_5, _gate_q_6, _gate_q_2;
  rz(pi/8) _gate_q_6;
  h _gate_q_5;
  p(pi/8) _gate_q_0;
  p(pi/8) _gate_q_1;
  p(pi/8) _gate_q_2;
  p(pi/8) _gate_q_5;
  cx _gate_q_0, _gate_q_1;
  p(-pi/8) _gate_q_1;
  cx _gate_q_0, _gate_q_1;
  cx _gate_q_1, _gate_q_2;
  p(-pi/8) _gate_q_2;
  cx _gate_q_0, _gate_q_2;
  p(pi/8) _gate_q_2;
  cx _gate_q_1, _gate_q_2;
  p(-pi/8) _gate_q_2;
  cx _gate_q_0, _gate_q_2;
  cx _gate_q_2, _gate_q_5;
  p(-pi/8) _gate_q_5;
  cx _gate_q_1, _gate_q_5;
  p(pi/8) _gate_q_5;
  cx _gate_q_2, _gate_q_5;
  p(-pi/8) _gate_q_5;
  cx _gate_q_0, _gate_q_5;
  p(pi/8) _gate_q_5;
  cx _gate_q_2, _gate_q_5;
  p(-pi/8) _gate_q_5;
  cx _gate_q_1, _gate_q_5;
  p(pi/8) _gate_q_5;
  cx _gate_q_2, _gate_q_5;
  p(-pi/8) _gate_q_5;
  cx _gate_q_0, _gate_q_5;
  h _gate_q_5;
  rz(-pi/16) _gate_q_5;
  mcx_vchain_dg_3 _gate_q_3, _gate_q_4, _gate_q_5;
  rz(pi/16) _gate_q_5;
  mcx_vchain_4 _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_5, _gate_q_3;
  rz(-pi/16) _gate_q_5;
  mcx_vchain_5 _gate_q_3, _gate_q_4, _gate_q_5;
  rz(pi/16) _gate_q_5;
  ccx _gate_q_0, _gate_q_1, _gate_q_4;
  rz(-pi/32) _gate_q_4;
  mcx_vchain_dg_6 _gate_q_2, _gate_q_3, _gate_q_4;
  rz(pi/32) _gate_q_4;
  mcx_vchain_7 _gate_q_0, _gate_q_1, _gate_q_4;
  rz(-pi/32) _gate_q_4;
  mcx_vchain_8 _gate_q_2, _gate_q_3, _gate_q_4;
  rz(pi/32) _gate_q_4;
  ccx _gate_q_0, _gate_q_1, _gate_q_3;
  rz(-pi/64) _gate_q_3;
  mcx_vchain_dg_9 _gate_q_2, _gate_q_3;
  rz(pi/64) _gate_q_3;
  mcx_vchain_10 _gate_q_0, _gate_q_1, _gate_q_3;
  rz(-pi/64) _gate_q_3;
  mcx_vchain_11 _gate_q_2, _gate_q_3;
  rz(pi/64) _gate_q_3;
  cx _gate_q_0, _gate_q_2;
  rz(-pi/128) _gate_q_2;
  mcx_vchain_dg_12 _gate_q_1, _gate_q_2;
  rz(pi/128) _gate_q_2;
  mcx_vchain_13 _gate_q_0, _gate_q_2;
  rz(-pi/128) _gate_q_2;
  mcx_vchain_14 _gate_q_1, _gate_q_2;
  rz(pi/128) _gate_q_2;
  crz(pi/64) _gate_q_0, _gate_q_1;
  p(pi/128) _gate_q_0;
}
gate mcx _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3, _gate_q_4, _gate_q_5, _gate_q_6, _gate_q_7 {
  h _gate_q_7;
  mcphase(pi) _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3, _gate_q_4, _gate_q_5, _gate_q_6, _gate_q_7;
  h _gate_q_7;
}
gate or _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3, _gate_q_4, _gate_q_5, _gate_q_6, _gate_q_7 {
  x _gate_q_7;
  x _gate_q_0;
  x _gate_q_1;
  x _gate_q_2;
  x _gate_q_3;
  x _gate_q_4;
  x _gate_q_5;
  x _gate_q_6;
  mcx _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3, _gate_q_4, _gate_q_5, _gate_q_6, _gate_q_7;
  x _gate_q_0;
  x _gate_q_1;
  x _gate_q_2;
  x _gate_q_3;
  x _gate_q_4;
  x _gate_q_5;
  x _gate_q_6;
}
qubit[7] in_0;
qubit[1] out;
or in_0[0], in_0[1], in_0[2], in_0[3], in_0[4], in_0[5], in_0[6], out[0];
'''
    ok, score, report = universal_check(qasm_string, n=7)
    print(ok, score)
    print(report)
