set_option maxHeartbeats 0
set_option maxRecDepth 1000000
def cellI (k : Nat) : Nat := (k * 7919 + 104729) % 268435456
def tabA : Array Nat := Array.ofFn (n := 512) fun k => cellI k
theorem a0 : tabA[511]! = 4151338 := by decide +kernel
