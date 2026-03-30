# Quantum Workflow Report
**Overall Status:** Success

## User Request
> Calibrate device: set qubit-8 frequency to 5.66e9, then Use QRNG to generate 10 random qubits, split into two 5-qubit registers, add them with the quantum adder to get a 5-bit number (abandon the cout), then apply permutation by 1 bit.

## Calibration
- Request: calibrate qubit-8 with new frequency 5.66e9
- Status: Success
```text
successfully calibrated!
```

## Qubit Usage
- **qrng_0** (qrng): logical=10, resource=10 — _Generating 10 random qubits requires 10 physical qubits; no ancilla needed._
- **adder_1** (adder): logical=5, resource=12 — _For a 5-bit addition using full adders, we need 2*5 + 2 = 12 qubits (5 for each input, 1 carry-in, 1 carry-out)._
- **permutation_2** (permutation): logical=5, resource=5 — _Permuting 5 qubits requires 5 qubits, no additional ancillas._

**Total resource qubits:** 27

## Data Transfers (Edges)
- qrng_0 → adder_1 (in=10, out=12): Direct state transfer of 10 qubits from QRNG split into two 5-qubit registers to the adder; includes 1-bit carry-in and 1-bit carry-out.
- adder_1 → permutation_2 (in=5, out=5): Amplitude encoding of 5-bit sum from adder into a 5-qubit register for permutation.

## QASM Artifacts
### Node qrng_0 (qrng)
```qasm
OPENQASM 3.0;
include "stdgates.inc";
bit[10] c;
qubit[10] q;
h q[0];
h q[1];
h q[2];
h q[3];
h q[4];
h q[5];
h q[6];
h q[7];
h q[8];
h q[9];
c[0] = measure q[0];
c[1] = measure q[1];
c[2] = measure q[2];
c[3] = measure q[3];
c[4] = measure q[4];
c[5] = measure q[5];
c[6] = measure q[6];
c[7] = measure q[7];
c[8] = measure q[8];
c[9] = measure q[9];
```
### Node adder_1 (adder)
```qasm
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
```
### Node permutation_2 (permutation)
```qasm
OPENQASM 3.0;
include "stdgates.inc";
gate permutation__1_2_3_4_0_ _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3, _gate_q_4 {
  swap _gate_q_3, _gate_q_4;
  swap _gate_q_2, _gate_q_4;
  swap _gate_q_1, _gate_q_4;
  swap _gate_q_0, _gate_q_4;
}
qubit[5] q;
permutation__1_2_3_4_0_ q[0], q[1], q[2], q[3], q[4];
```