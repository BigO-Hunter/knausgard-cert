set_option maxHeartbeats 0
set_option maxRecDepth 1000000
def cellI (k : Nat) : Nat := (k * 7919 + 104729) % 268435456
def tabA : Array Nat := Array.ofFn (n := 1024) fun k => cellI k
theorem a0 : tabA[1023]! = 8205866 := by decide +kernel
