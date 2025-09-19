OPENQASM 3.0;
include "stdgates.inc";
gate permutation__1_2_3_4_5_0_ _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3, _gate_q_4, _gate_q_5 {
  swap _gate_q_4, _gate_q_5;
  swap _gate_q_3, _gate_q_5;
  swap _gate_q_2, _gate_q_5;
  swap _gate_q_1, _gate_q_5;
  swap _gate_q_0, _gate_q_5;
}
qubit[6] q;
permutation__1_2_3_4_5_0_ q[0], q[1], q[2], q[3], q[4], q[5];
