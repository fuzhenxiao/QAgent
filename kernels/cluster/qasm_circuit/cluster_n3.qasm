OPENQASM 3.0;
include "stdgates.inc";
qubit[3] q;
h q[0];
h q[1];
h q[2];
cz q[0], q[1];
cz q[1], q[2];
