OPENQASM 3.0;
include "stdgates.inc";
gate Oracle _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3, _gate_q_4 {
  x _gate_q_2;
  cx _gate_q_0, _gate_q_4;
  cx _gate_q_1, _gate_q_4;
  cx _gate_q_2, _gate_q_4;
  cx _gate_q_3, _gate_q_4;
  x _gate_q_2;
}
bit[4] c;
qubit[5] q;
h q[0];
h q[1];
h q[2];
h q[3];
x q[4];
h q[4];
Oracle q[0], q[1], q[2], q[3], q[4];
h q[0];
h q[1];
h q[2];
h q[3];
c[0] = measure q[0];
c[1] = measure q[1];
c[2] = measure q[2];
c[3] = measure q[3];
