defcalgrammar "openpulse";

const float q0_freq = 4762541968.964;
const float q1_freq = 4906285411.793;
const float q2_freq = 4960974437.546;
const float q3_freq = 4962370616.586;
const float q4_freq = 5090426673.931;
const float q5_freq = 5011254700.781;
const float q6_freq = 4960977173.842;
const float q7_freq = 4922763717.865;
const float q8_freq = 4831194813.278;
const float q9_freq = 5660000000.000;
const float q10_freq = 4764616049.777;
const float q11_freq = 4909269545.912;
const float q12_freq = 5082785692.169;
const float q13_freq = 5107948089.683;
const float q14_freq = 5127905788.192;
const float q15_freq = 5040327045.261;
const float q16_freq = 4922378374.405;
const float q17_freq = 4808167737.096;
const float q18_freq = 4712513694.581;
const float q19_freq = 4976955949.805;
const float q20_freq = 5244274794.820;
const float q21_freq = 4921754269.011;
const float q22_freq = 5018487098.285;
const float q23_freq = 4681119959.224;
const float q24_freq = 5253838309.401;
const float q25_freq = 5052374555.418;
const float q26_freq = 4782376020.995;

const float ro0_freq = 6523077762.657;
const float ro1_freq = 6555213350.158;
const float ro2_freq = 6153579670.061;
const float ro3_freq = 6320137632.326;
const float ro4_freq = 6454013987.593;
const float ro5_freq = 6370129643.603;
const float ro6_freq = 6413558145.228;
const float ro7_freq = 6394051203.387;
const float ro8_freq = 6426529239.775;
const float ro9_freq = 6405863935.996;
const float ro10_freq = 6276140730.078;
const float ro11_freq = 6332413231.177;
const float ro12_freq = 6515310899.826;
const float ro13_freq = 6378405677.924;
const float ro14_freq = 6232079932.516;
const float ro15_freq = 6367821954.756;
const float ro16_freq = 6500731877.682;
const float ro17_freq = 6425290987.649;
const float ro18_freq = 6278361382.957;
const float ro19_freq = 6286806179.899;
const float ro20_freq = 6436546110.795;
const float ro21_freq = 6467067945.509;
const float ro22_freq = 6357747687.620;
const float ro23_freq = 6475127963.149;
const float ro24_freq = 6278226900.606;
const float ro25_freq = 6481465294.595;
const float ro26_freq = 6179312894.607;

const duration x_len = 160dt;
const duration sx_len = 160dt;
const duration gauss_sigma = 40dt;
const duration cr_len = 560dt;
const duration cr_sigma = 40dt;
const duration cr_square = 240dt;
const float x_amp = 0.2;
const float sx_amp = 0.1;
const float beta = 0.1;

cal {
   extern drag(complex[size] amp, duration l, duration sigma, float[size] beta) -> waveform;
   extern gaussian_square(complex[size] amp, duration l, duration square_width, duration sigma) -> waveform;
   extern drag_gaussian(complex[size] amp, duration l, duration sigma, float[size] beta) -> waveform; // alias

   extern port q0;
   extern port q1;
   extern port q2;
   extern port q3;
   extern port q4;
   extern port q5;
   extern port q6;
   extern port q7;
   extern port q8;
   extern port q9;
   extern port q10;
   extern port q11;
   extern port q12;
   extern port q13;
   extern port q14;
   extern port q15;
   extern port q16;
   extern port q17;
   extern port q18;
   extern port q19;
   extern port q20;
   extern port q21;
   extern port q22;
   extern port q23;
   extern port q24;
   extern port q25;
   extern port q26;

   frame q0_frame = newframe(q0, q0_freq, 0);
   frame q1_frame = newframe(q1, q1_freq, 0);
   frame q2_frame = newframe(q2, q2_freq, 0);
   frame q3_frame = newframe(q3, q3_freq, 0);
   frame q4_frame = newframe(q4, q4_freq, 0);
   frame q5_frame = newframe(q5, q5_freq, 0);
   frame q6_frame = newframe(q6, q6_freq, 0);
   frame q7_frame = newframe(q7, q7_freq, 0);
   frame q8_frame = newframe(q8, q8_freq, 0);
   frame q9_frame = newframe(q9, q9_freq, 0);
   frame q10_frame = newframe(q10, q10_freq, 0);
   frame q11_frame = newframe(q11, q11_freq, 0);
   frame q12_frame = newframe(q12, q12_freq, 0);
   frame q13_frame = newframe(q13, q13_freq, 0);
   frame q14_frame = newframe(q14, q14_freq, 0);
   frame q15_frame = newframe(q15, q15_freq, 0);
   frame q16_frame = newframe(q16, q16_freq, 0);
   frame q17_frame = newframe(q17, q17_freq, 0);
   frame q18_frame = newframe(q18, q18_freq, 0);
   frame q19_frame = newframe(q19, q19_freq, 0);
   frame q20_frame = newframe(q20, q20_freq, 0);
   frame q21_frame = newframe(q21, q21_freq, 0);
   frame q22_frame = newframe(q22, q22_freq, 0);
   frame q23_frame = newframe(q23, q23_freq, 0);
   frame q24_frame = newframe(q24, q24_freq, 0);
   frame q25_frame = newframe(q25, q25_freq, 0);
   frame q26_frame = newframe(q26, q26_freq, 0);
}

// ---------- Drive-frame resolver ----------
defcal _resolve_drive_frame $0  -> frame f { f = d0; }
defcal _resolve_drive_frame $1  -> frame f { f = d1; }
defcal _resolve_drive_frame $2  -> frame f { f = d2; }
defcal _resolve_drive_frame $3  -> frame f { f = d3; }
defcal _resolve_drive_frame $4  -> frame f { f = d4; }
defcal _resolve_drive_frame $5  -> frame f { f = d5; }
defcal _resolve_drive_frame $6  -> frame f { f = d6; }
defcal _resolve_drive_frame $7  -> frame f { f = d7; }
defcal _resolve_drive_frame $8  -> frame f { f = d8; }
defcal _resolve_drive_frame $9  -> frame f { f = d9; }
defcal _resolve_drive_frame $10 -> frame f { f = d10; }
defcal _resolve_drive_frame $11 -> frame f { f = d11; }
defcal _resolve_drive_frame $12 -> frame f { f = d12; }
defcal _resolve_drive_frame $13 -> frame f { f = d13; }
defcal _resolve_drive_frame $14 -> frame f { f = d14; }
defcal _resolve_drive_frame $15 -> frame f { f = d15; }
defcal _resolve_drive_frame $16 -> frame f { f = d16; }
defcal _resolve_drive_frame $17 -> frame f { f = d17; }
defcal _resolve_drive_frame $18 -> frame f { f = d18; }
defcal _resolve_drive_frame $19 -> frame f { f = d19; }
defcal _resolve_drive_frame $20 -> frame f { f = d20; }
defcal _resolve_drive_frame $21 -> frame f { f = d21; }
defcal _resolve_drive_frame $22 -> frame f { f = d22; }
defcal _resolve_drive_frame $23 -> frame f { f = d23; }
defcal _resolve_drive_frame $24 -> frame f { f = d24; }
defcal _resolve_drive_frame $25 -> frame f { f = d25; }
defcal _resolve_drive_frame $26 -> frame f { f = d26; }

// ---------- Readout-frame resolver ----------
defcal _resolve_ro_frame $0  -> frame f { f = r0; }
defcal _resolve_ro_frame $1  -> frame f { f = r1; }
defcal _resolve_ro_frame $2  -> frame f { f = r2; }
defcal _resolve_ro_frame $3  -> frame f { f = r3; }
defcal _resolve_ro_frame $4  -> frame f { f = r4; }
defcal _resolve_ro_frame $5  -> frame f { f = r5; }
defcal _resolve_ro_frame $6  -> frame f { f = r6; }
defcal _resolve_ro_frame $7  -> frame f { f = r7; }
defcal _resolve_ro_frame $8  -> frame f { f = r8; }
defcal _resolve_ro_frame $9  -> frame f { f = r9; }
defcal _resolve_ro_frame $10 -> frame f { f = r10; }
defcal _resolve_ro_frame $11 -> frame f { f = r11; }
defcal _resolve_ro_frame $12 -> frame f { f = r12; }
defcal _resolve_ro_frame $13 -> frame f { f = r13; }
defcal _resolve_ro_frame $14 -> frame f { f = r14; }
defcal _resolve_ro_frame $15 -> frame f { f = r15; }
defcal _resolve_ro_frame $16 -> frame f { f = r16; }
defcal _resolve_ro_frame $17 -> frame f { f = r17; }
defcal _resolve_ro_frame $18 -> frame f { f = r18; }
defcal _resolve_ro_frame $19 -> frame f { f = r19; }
defcal _resolve_ro_frame $20 -> frame f { f = r20; }
defcal _resolve_ro_frame $21 -> frame f { f = r21; }
defcal _resolve_ro_frame $22 -> frame f { f = r22; }
defcal _resolve_ro_frame $23 -> frame f { f = r23; }
defcal _resolve_ro_frame $24 -> frame f { f = r24; }
defcal _resolve_ro_frame $25 -> frame f { f = r25; }
defcal _resolve_ro_frame $26 -> frame f { f = r26; }

// ---------- Public generic helpers ----------
// Keep your gate code calling these generic names:
defcal _resolve_frame $q -> frame f {
  _resolve_drive_frame $q -> f;
}

defcal _resolve_measure_frame $q -> frame f {
  _resolve_ro_frame $q -> f;
}


defcal rz(float theta) $q {
   frame f; _resolve_frame $q -> f;
   shiftphase(f, theta);
}

defcal p(float lambda) $q {
   rz(lambda) $q;
}

defcal x $q {
   frame f; _resolve_frame $q -> f;
   waveform wf = drag(x_amp + 0.05im, x_len, gauss_sigma, beta);
   play(f, wf);
}

defcal sx $q {
   frame f; _resolve_frame $q -> f;
   waveform wf = drag(sx_amp + 0.05im, sx_len, gauss_sigma, beta);
   play(f, wf);
}

defcal y $q {
   rz(pi/2) $q;
   x $q;
   rz(-pi/2) $q;
}

defcal z $q {
   rz(pi) $q;
}

defcal h $q {
  rz(pi/2) $q;
  sx $q;               // sx == rx(pi/2)
  rz(pi/2) $q;
}


defcal s $q { rz(pi/2) $q; }
defcal sdg $q { rz(-pi/2) $q; }
defcal t $q { rz(pi/4) $q; }
defcal tdg $q { rz(-pi/4) $q; }

defcal rx(angle[32] theta) $q {
    rz(pi/2) $q;
    sx $q;
    rz(pi-theta) $q;
    sx $q;
    rz(pi/2) $q;
}

defcal ry(float theta) $q {
   // Rotate around Y using X plus phase-wrapping
   rz(pi/2) $q;
   rx(theta) $q;
   rz(-pi/2) $q;
}


defcal xrz(float theta, float phi) $q {
   rx(theta) $q;
   rz(phi) $q;
}

// Cross-resonance-based entangling template used for CX, CY, CZ, CP, CRX, CRY, CH, CU, SWAP, CSWAP, CCX builds
defcal _cr90_pulse $c, $t {
   frame fc; _resolve_frame $c -> fc;
   waveform CR90p = gaussian_square(0.22 + 0.05im, cr_len, cr_square, cr_sigma);
   play(fc, CR90p);
}
defcal _cr90m_pulse $c, $t {
   frame fc; _resolve_frame $c -> fc;
   waveform CR90m = gaussian_square(-0.22 - 0.05im, cr_len, cr_square, cr_sigma);
   play(fc, CR90m);
}

defcal cx $c, $t {
   // Echoed-CR with single-qubit dressing (illustrative):
   rz(pi/2) $t; rz(-pi/2) $c;
   sx $c; sx $t;
   barrier $c, $t;
   _cr90_pulse $c, $t;
   barrier $c, $t;
   x $c;
   barrier $c, $t;
   _cr90m_pulse $c, $t;
   rz(-pi/2) $t; rz(pi/2) $c;
   sx $c; sx $t;
}

defcal cy $c, $t {
   // CY = (S on target) CX (Sdg on target)
   s $t;
   cx $c, $t;
   sdg $t;
}

defcal cz $c, $t {
   // CZ = (H on target) CX (H on target)
   h $t;
   cx $c, $t;
   h $t;
}

defcal cp(float lambda) $c, $t {
   // CP = [SX on t] CR phase-dressed ... approximated via CZ + RZ
   cz $c, $t;
   rz(lambda/2) $c;
   rz(lambda/2) $t;
}

defcal crx(float theta) $c, $t {
   // Use two CX with single-qubit rotations (illustrative):
   ry(-theta/2) $t;
   cx $c, $t;
   ry(theta/2) $t;
   cx $c, $t;
}

defcal cry(float theta) $c, $t {
   rx(theta/2) $t;
   cx $c, $t;
   rx(-theta/2) $t;
   cx $c, $t;
}

defcal ch $c, $t {
   s $t;
   h $t;
   cx $c, $t;
   h $t; sdg $t;
}

defcal cu(float theta, float phi, float lam, float gamma) $c, $t {
   // Decompose CU using 2 CX and single-qubit rotations (illustrative)
   rz((phi+lam)/2) $t;
   rx(pi/2) $t;
   cx $c, $t;
   rz(-(phi+lam)/2) $t;
   rx(-pi/2) $t;
   rz(-(phi-lam)/2) $t;
   rz(-gamma/2) $c;
   cx $c, $t;
   rz(gamma/2) $c;
   rz((phi-lam)/2) $t;
}

defcal swap $a, $b {
   cx $a, $b;
   cx $b, $a;
   cx $a, $b;
}

defcal ccx $a, $b, $t {
   // Simplified textbook Toffoli using 6 CX and 1-qubit rotations (illustrative)
   h $t;
   cx $b, $t;
   tdg $t;
   cx $a, $t;
   t $t;
   cx $b, $t;
   tdg $t;
   cx $a, $t;
   t $b; t $t;
   h $t;
   cx $a, $b;
   t $a; sdg $b;
   cx $a, $b;
}

defcal cswap $c, $a, $b {
   cx $b, $a;
   ccx $c, $a, $b;
   ccx $c, $b, $a;
   cx $b, $a;
}

// Readout calibration stubs
defcal measure $q -> bit c {
  frame rf; _resolve_ro_frame $q -> rf;
  play(rf, ro_pulse);
  capture(rf, ro_kernel) -> c;
}


