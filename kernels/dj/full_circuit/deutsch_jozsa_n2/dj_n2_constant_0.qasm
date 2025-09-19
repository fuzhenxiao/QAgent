OPENQASM 3.0;
include "stdgates.inc";
gate Oracle _gate_q_0, _gate_q_1, _gate_q_2 {
  id _gate_q_2;
}
bit[2] c;
qubit[3] q;
h q[0];
h q[1];
x q[2];
h q[2];
Oracle q[0], q[1], q[2];
h q[0];
h q[1];
c[0] = measure q[0];
c[1] = measure q[1];
