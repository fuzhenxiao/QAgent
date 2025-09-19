OPENQASM 3.0;
include "stdgates.inc";
gate permutation__1_2_0_ _gate_q_0, _gate_q_1, _gate_q_2 {
  swap _gate_q_1, _gate_q_2;
  swap _gate_q_0, _gate_q_2;
}
qubit[3] q;
permutation__1_2_0_ q[0], q[1], q[2];
