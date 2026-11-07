import RepD
set_option maxHeartbeats 0
set_option maxRecDepth 1000000
theorem pd0 : getD 99693 = 271477 := by decide +kernel
theorem pd1 : getD 148007 = 2794 := by decide +kernel
theorem pd2 : getD 173242 = 167685 := by decide +kernel
