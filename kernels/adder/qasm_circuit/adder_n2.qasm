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
gate FullAdder _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3, _gate_q_4, _gate_q_5 {
  MAJ _gate_q_1, _gate_q_3, _gate_q_0;
  MAJ _gate_q_2, _gate_q_4, _gate_q_1;
  cx _gate_q_2, _gate_q_5;
  UMA _gate_q_2, _gate_q_4, _gate_q_1;
  UMA _gate_q_1, _gate_q_3, _gate_q_0;
}
qubit[2] a;
qubit[2] b;
qubit[1] cin;
qubit[1] cout;
FullAdder a[0], a[1], b[0], b[1], cin[0], cout[0];
