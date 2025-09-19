OPENQASM 3.0;
include "stdgates.inc";
qubit[2] q;
h q[0];
h q[1];
cz q[0], q[1];
