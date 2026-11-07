set_option maxHeartbeats 0
set_option maxRecDepth 100000
def cellI (k : Nat) : Nat := (k * 7919 + 104729) % 268435456
def tabA : Array Nat := Array.ofFn (n := 209010) fun k => cellI k
