import RepE
set_option maxHeartbeats 0
set_option maxRecDepth 1000000
theorem pe0 : getE 99693 = 271477 := by decide +kernel
theorem pe1 : getE 148007 = 2794 := by decide +kernel
theorem pe2 : getE 173242 = 167685 := by decide +kernel
