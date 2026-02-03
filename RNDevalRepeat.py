#%% 
# Proof-of-principle implementation for anonymous review
# This software is provided for research and evaluation purposes only. Licensing terms may change.
# Copyright (c) 2026

import itertools, math
from datetime import datetime
# ---------- small helpers ----------
def rule(A, B): return [A, B]
def rewriting_system(rules): return [rule(*r) for r in rules]
def pretty_print_rs(rules):
    print("Rewriting System of complexity", rsComplexity(rules))
    for lhs, rhs in rules: print(f"  {lhs} -> {rhs}")

#%% parameters and input reading, process all strings in xlist.txt
max_len = 8 # max length of LHS and RHS in rules 
thrRandomness = -13 # threshold for randomness alarm
print("this is only a placeholder for RNDevalRepeat.py")
print("will fill up later")