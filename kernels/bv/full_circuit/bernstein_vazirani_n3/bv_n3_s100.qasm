OPENQASM 3.0;
include "stdgates.inc";
gate Oracle _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3 {
  cx _gate_q_2, _gate_q_3;
}
bit[3] c;
qubit[4] q;
h q[0];
h q[1];
h q[2];
x q[3];
h q[3];
Oracle q[0], q[1], q[2], q[3];
h q[0];
h q[1];
h q[2];
c[0] = measure q[0];
c[1] = measure q[1];
c[2] = measure q[2];
