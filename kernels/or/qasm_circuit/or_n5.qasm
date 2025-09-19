OPENQASM 3.0;
include "stdgates.inc";
gate mcx_vchain_dg _gate_q_0, _gate_q_1, _gate_q_2 {
  ccx _gate_q_0, _gate_q_1, _gate_q_2;
}
gate mcx_vchain _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3, _gate_q_4 {
  h _gate_q_3;
  p(pi/8) _gate_q_0;
  p(pi/8) _gate_q_1;
  p(pi/8) _gate_q_2;
  p(pi/8) _gate_q_3;
  cx _gate_q_0, _gate_q_1;
  p(-pi/8) _gate_q_1;
  cx _gate_q_0, _gate_q_1;
  cx _gate_q_1, _gate_q_2;
  p(-pi/8) _gate_q_2;
  cx _gate_q_0, _gate_q_2;
  p(pi/8) _gate_q_2;
  cx _gate_q_1, _gate_q_2;
  p(-pi/8) _gate_q_2;
  cx _gate_q_0, _gate_q_2;
  cx _gate_q_2, _gate_q_3;
  p(-pi/8) _gate_q_3;
  cx _gate_q_1, _gate_q_3;
  p(pi/8) _gate_q_3;
  cx _gate_q_2, _gate_q_3;
  p(-pi/8) _gate_q_3;
  cx _gate_q_0, _gate_q_3;
  p(pi/8) _gate_q_3;
  cx _gate_q_2, _gate_q_3;
  p(-pi/8) _gate_q_3;
  cx _gate_q_1, _gate_q_3;
  p(pi/8) _gate_q_3;
  cx _gate_q_2, _gate_q_3;
  p(-pi/8) _gate_q_3;
  cx _gate_q_0, _gate_q_3;
  h _gate_q_3;
}
gate mcx_vchain_0 _gate_q_0, _gate_q_1, _gate_q_2 {
  ccx _gate_q_0, _gate_q_1, _gate_q_2;
}
gate mcx_vchain_1 _gate_q_0, _gate_q_1, _gate_q_2 {
  ccx _gate_q_0, _gate_q_1, _gate_q_2;
}
gate mcx_vchain_2 _gate_q_0, _gate_q_1, _gate_q_2 {
  ccx _gate_q_0, _gate_q_1, _gate_q_2;
}
gate mcx_vchain_dg_3 _gate_q_0, _gate_q_1 {
  cx _gate_q_0, _gate_q_1;
}
gate mcx_vchain_4 _gate_q_0, _gate_q_1, _gate_q_2 {
  ccx _gate_q_0, _gate_q_1, _gate_q_2;
}
gate mcx_vchain_5 _gate_q_0, _gate_q_1 {
  cx _gate_q_0, _gate_q_1;
}
gate mcx_vchain_dg_6 _gate_q_0, _gate_q_1 {
  cx _gate_q_0, _gate_q_1;
}
gate mcx_vchain_7 _gate_q_0, _gate_q_1 {
  cx _gate_q_0, _gate_q_1;
}
gate mcx_vchain_8 _gate_q_0, _gate_q_1 {
  cx _gate_q_0, _gate_q_1;
}
gate mcphase(_gate_p_0) _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3, _gate_q_4, _gate_q_5 {
  h _gate_q_5;
  p(pi/8) _gate_q_0;
  p(pi/8) _gate_q_1;
  p(pi/8) _gate_q_2;
  p(pi/8) _gate_q_5;
  cx _gate_q_0, _gate_q_1;
  p(-pi/8) _gate_q_1;
  cx _gate_q_0, _gate_q_1;
  cx _gate_q_1, _gate_q_2;
  p(-pi/8) _gate_q_2;
  cx _gate_q_0, _gate_q_2;
  p(pi/8) _gate_q_2;
  cx _gate_q_1, _gate_q_2;
  p(-pi/8) _gate_q_2;
  cx _gate_q_0, _gate_q_2;
  cx _gate_q_2, _gate_q_5;
  p(-pi/8) _gate_q_5;
  cx _gate_q_1, _gate_q_5;
  p(pi/8) _gate_q_5;
  cx _gate_q_2, _gate_q_5;
  p(-pi/8) _gate_q_5;
  cx _gate_q_0, _gate_q_5;
  p(pi/8) _gate_q_5;
  cx _gate_q_2, _gate_q_5;
  p(-pi/8) _gate_q_5;
  cx _gate_q_1, _gate_q_5;
  p(pi/8) _gate_q_5;
  cx _gate_q_2, _gate_q_5;
  p(-pi/8) _gate_q_5;
  cx _gate_q_0, _gate_q_5;
  h _gate_q_5;
  rz(-pi/4) _gate_q_5;
  mcx_vchain_dg _gate_q_3, _gate_q_4, _gate_q_5;
  rz(pi/4) _gate_q_5;
  mcx_vchain _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_5, _gate_q_3;
  rz(-pi/4) _gate_q_5;
  mcx_vchain_0 _gate_q_3, _gate_q_4, _gate_q_5;
  rz(pi/4) _gate_q_5;
  ccx _gate_q_0, _gate_q_1, _gate_q_4;
  rz(-pi/8) _gate_q_4;
  mcx_vchain_dg _gate_q_2, _gate_q_3, _gate_q_4;
  rz(pi/8) _gate_q_4;
  mcx_vchain_1 _gate_q_0, _gate_q_1, _gate_q_4;
  rz(-pi/8) _gate_q_4;
  mcx_vchain_2 _gate_q_2, _gate_q_3, _gate_q_4;
  rz(pi/8) _gate_q_4;
  ccx _gate_q_0, _gate_q_1, _gate_q_3;
  rz(-pi/16) _gate_q_3;
  mcx_vchain_dg_3 _gate_q_2, _gate_q_3;
  rz(pi/16) _gate_q_3;
  mcx_vchain_4 _gate_q_0, _gate_q_1, _gate_q_3;
  rz(-pi/16) _gate_q_3;
  mcx_vchain_5 _gate_q_2, _gate_q_3;
  rz(pi/16) _gate_q_3;
  cx _gate_q_0, _gate_q_2;
  rz(-pi/32) _gate_q_2;
  mcx_vchain_dg_6 _gate_q_1, _gate_q_2;
  rz(pi/32) _gate_q_2;
  mcx_vchain_7 _gate_q_0, _gate_q_2;
  rz(-pi/32) _gate_q_2;
  mcx_vchain_8 _gate_q_1, _gate_q_2;
  rz(pi/32) _gate_q_2;
  crz(pi/16) _gate_q_0, _gate_q_1;
  p(pi/32) _gate_q_0;
}
gate mcx _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3, _gate_q_4, _gate_q_5 {
  h _gate_q_5;
  mcphase(pi) _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3, _gate_q_4, _gate_q_5;
  h _gate_q_5;
}
gate or _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3, _gate_q_4, _gate_q_5 {
  x _gate_q_5;
  x _gate_q_0;
  x _gate_q_1;
  x _gate_q_2;
  x _gate_q_3;
  x _gate_q_4;
  mcx _gate_q_0, _gate_q_1, _gate_q_2, _gate_q_3, _gate_q_4, _gate_q_5;
  x _gate_q_0;
  x _gate_q_1;
  x _gate_q_2;
  x _gate_q_3;
  x _gate_q_4;
}
qubit[5] in_0;
qubit[1] out;
or in_0[0], in_0[1], in_0[2], in_0[3], in_0[4], out[0];
