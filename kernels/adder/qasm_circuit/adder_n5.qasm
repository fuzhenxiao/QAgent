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
gate FullAdder _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3, _gate_q_4, _gate_q_5, _gate_q_6, _gate_q_7, _gate_q_8, _gate_q_9, _gate_q_10, _gate_q_11 {
  MAJ _gate_q_1, _gate_q_6, _gate_q_0;
  MAJ _gate_q_2, _gate_q_7, _gate_q_1;
  MAJ _gate_q_3, _gate_q_8, _gate_q_2;
  MAJ _gate_q_4, _gate_q_9, _gate_q_3;
  MAJ _gate_q_5, _gate_q_10, _gate_q_4;
  cx _gate_q_5, _gate_q_11;
  UMA _gate_q_5, _gate_q_10, _gate_q_4;
  UMA _gate_q_4, _gate_q_9, _gate_q_3;
  UMA _gate_q_3, _gate_q_8, _gate_q_2;
  UMA _gate_q_2, _gate_q_7, _gate_q_1;
  UMA _gate_q_1, _gate_q_6, _gate_q_0;
}
qubit[5] a;
qubit[5] b;
qubit[1] cin;
qubit[1] cout;
FullAdder a[0], a[1], a[2], a[3], a[4], b[0], b[1], b[2], b[3], b[4], cin[0], cout[0];
