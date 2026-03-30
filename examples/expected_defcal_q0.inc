defcalgrammar "openpulse";

cal {
    float base_freq_q0 = 5.2e9;
    float delta_q0 = 1.0e5;
    // drift added here
    float calibrated_freq_q0 =
        base_freq_q0 + delta_q0;

    extern port d0;
    frame fr_q0 = newframe(d0,
        calibrated_freq_q0, 0.0);
}
