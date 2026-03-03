#%% 
# Proof-of-principle research implementation corresponding to a research article
# Provided solely for research and evaluation purposes.
#
# Copyright (c) 2026
# See the LICENSE file for full terms.

import itertools, math
from datetime import datetime
# ---------- small helpers ----------
def rule(A, B): return [A, B]
def rewriting_system(rules): return [rule(*r) for r in rules]
def pretty_print_rs(rules):
    print("Rewriting System of complexity", rsComplexity(rules))
    for lhs, rhs in rules: print(f"  {lhs} -> {rhs}")

# Entry point for proof-of-principle execution
def main():
    # Proof-of-principle execution example
    #%% parameters 
    max_len = 8 # max length of LHS and RHS in rules 
    thrRandomness = -13 # threshold for randomness alarm
    print("this is only a placeholder for RNDevalRepeat.py")
    print("will fill up later")

if __name__ == "__main__":
    main()
