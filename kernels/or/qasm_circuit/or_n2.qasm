OPENQASM 3.0;
include "stdgates.inc";
gate or _gate_q_0, _gate_q_1, _gate_q_2 {
  x _gate_q_2;
  x _gate_q_0;
  x _gate_q_1;
  ccx _gate_q_0, _gate_q_1, _gate_q_2;
  x _gate_q_0;
  x _gate_q_1;
}
qubit[2] in_0;
qubit[1] out;
or in_0[0], in_0[1], out[0];
