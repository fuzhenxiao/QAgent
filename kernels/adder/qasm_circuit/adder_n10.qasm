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
gate FullAdder _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3, _gate_q_4, _gate_q_5, _gate_q_6, _gate_q_7, _gate_q_8, _gate_q_9, _gate_q_10, _gate_q_11, _gate_q_12, _gate_q_13, _gate_q_14, _gate_q_15, _gate_q_16, _gate_q_17, _gate_q_18, _gate_q_19, _gate_q_20, _gate_q_21 {
  MAJ _gate_q_1, _gate_q_11, _gate_q_0;
  MAJ _gate_q_2, _gate_q_12, _gate_q_1;
  MAJ _gate_q_3, _gate_q_13, _gate_q_2;
  MAJ _gate_q_4, _gate_q_14, _gate_q_3;
  MAJ _gate_q_5, _gate_q_15, _gate_q_4;
  MAJ _gate_q_6, _gate_q_16, _gate_q_5;
  MAJ _gate_q_7, _gate_q_17, _gate_q_6;
  MAJ _gate_q_8, _gate_q_18, _gate_q_7;
  MAJ _gate_q_9, _gate_q_19, _gate_q_8;
  MAJ _gate_q_10, _gate_q_20, _gate_q_9;
  cx _gate_q_10, _gate_q_21;
  UMA _gate_q_10, _gate_q_20, _gate_q_9;
  UMA _gate_q_9, _gate_q_19, _gate_q_8;
  UMA _gate_q_8, _gate_q_18, _gate_q_7;
  UMA _gate_q_7, _gate_q_17, _gate_q_6;
  UMA _gate_q_6, _gate_q_16, _gate_q_5;
  UMA _gate_q_5, _gate_q_15, _gate_q_4;
  UMA _gate_q_4, _gate_q_14, _gate_q_3;
  UMA _gate_q_3, _gate_q_13, _gate_q_2;
  UMA _gate_q_2, _gate_q_12, _gate_q_1;
  UMA _gate_q_1, _gate_q_11, _gate_q_0;
}
qubit[10] a;
qubit[10] b;
qubit[1] cin;
qubit[1] cout;
FullAdder a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7], a[8], a[9], b[0], b[1], b[2], b[3], b[4], b[5], b[6], b[7], b[8], b[9], cin[0], cout[0];
