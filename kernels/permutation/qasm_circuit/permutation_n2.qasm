OPENQASM 3.0;
include "stdgates.inc";
gate permutation__1_0_ _gate_q_0, _gate_q_1 {
  swap _gate_q_0, _gate_q_1;
}
qubit[2] q;
permutation__1_0_ q[0], q[1];
