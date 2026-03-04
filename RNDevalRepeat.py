#%% 
# Proof-of-principle research implementation corresponding to a research article
# Provided solely for research and evaluation purposes.
#
# Copyright (c) 2026
# See the LICENSE file for full terms.

#%% # backwardGen.py
import itertools, math
from datetime import datetime
# ---------- small helpers ----------
def rule(A, B): return [A, B]
def rewriting_system(rules): return [rule(*r) for r in rules]
def pretty_print_rs(rules):
    print("Rewriting System of complexity", rsComplexity(rules))
    for lhs, rhs in rules: print(f"  {lhs} -> {rhs}")
# ---------- complexity functions ----------
def gamma_length(n: int) -> int:
    if n < 1: raise ValueError("Gamma code is only defined for n >= 1")
    return 2 * (n.bit_length() - 1) + 1
def rsPrefixFreeComplexity(rules):
    r = len(rules); total = gamma_length(r) 
    for lhs, rhs in rules:
        total += gamma_length(len(lhs)) + len(lhs)
        total += gamma_length(len(rhs)) + len(rhs)
    return total
# Stop character complexity: encode bits, ->, end_of_rule
# as 00, 01, 10, 11. End of system as 11
def rsComplexityStopChar(rules):
    return 2*sum(len(lhs) + len(rhs) for lhs, rhs in rules)+2+4*len(rules)
def rsPrefixFreeComplexity_expanding(rules):
    """prefix-free encoding length (in bits) of system = rules
    where all rules are expanding (len(lhs) < len(rhs)). Rule encoding scheme:
      - rhs length: gamma-coded + rhs body bits
      - lhs length: fixed-width bits (ceil(log2(rhs_len - 1))) + lhs body bits
      - rule count: gamma-coded"""
    r = len(rules); total = gamma_length(r)  # rule count header
    for lhs, rhs in rules:
        lhs_len = len(lhs); rhs_len = len(rhs)
        if lhs_len >= rhs_len:
            raise ValueError("All rules must be expanding: lhs < rhs")
        # rhs: gamma header + rhs bits
        total += gamma_length(rhs_len) + rhs_len
        # lhs: fixed-width header + lhs bits
        lhs_header_bits = max(1, math.ceil(math.log2(rhs_len - 1)))
        total += lhs_header_bits + lhs_len
    return total
# ---------- rewriting application ----------
def apply_forward_rewriting(input_str, rules, max_steps):
    """Apply rewriting rules up to max_steps.
    Returns (output_str, steps, terminated)
    where terminated=True iff computation halted because no rule applied
    (not just because max_steps was reached)."""
    current = input_str; steps = 0
    while steps < max_steps:
        applied = False
        for lhs, rhs in rules:  # try rules in order
            for i in range(len(current) - len(lhs) + 1):
                if current[i:i+len(lhs)] == lhs:
                    current = current[:i] + rhs + current[i+len(lhs):]
                    applied = True; steps += 1
                    break  # leftmost match
            if applied: break
        if not applied: return current, steps, True  # halted normally
    return current, steps, False  # stopped due to max_steps
def apply_backward_rewriting(finalx, x, rules, max_steps):
    # Apply backward rewriting from x 
    # using rules, up to max_steps, deterministially 
    # (might not find all possible backward paths)
    ##################################
    # Check that finalx is terminal in the forward direction
    fwd_x, _, terminated = apply_forward_rewriting(finalx, rules, 1)
    if not terminated: return x, 0, False
    current = x; steps = 0
    while steps < max_steps:
        applied = False
        for lhs, rhs in rules:
            # search for rightmost rhs occurrences in current
            for pos in range(len(current) - len(rhs), -1, -1):
                if current[pos:pos+len(rhs)] == rhs:
                    cand = current[:pos] + lhs + current[pos+len(rhs):]
                    fwd, _, _ = apply_forward_rewriting(cand, rules, 1)
                    if fwd == current:
                        current = cand
                        applied = True
                        break  # stop scanning rhs positions
            if applied: break  # stop scanning rules only if something worked
        if not applied: break  # no backward step possible
        steps += 1
        if len(current) > len(x) * max_expansion:
            print("Termination condition 1: reached max string length")
            return current, steps, False
    return current, steps, True
#**********************************************************
def lazy_all_bin_upto_length(n):
    """Generate all binary strings of length 1..n lazily."""
    for l in range(1, n + 1):
        for bits in itertools.product('01', repeat=l):
            yield ''.join(bits)
def substrings_upto_length(CS, n):
    """Lazily generate all distinct substrings of CS of length 1..n."""
    seen = set(); L = len(CS)
    for length in range(1, n + 1):
        for start in range(L - length + 1):
            s = CS[start:start + length]
            if s not in seen:
                seen.add(s)
                yield s
def enumerate_rules(finalx, CS, max_len, require_expanding=True):
    # *********** to be finished and verified
    """Enumerate one rewriting rule with:
      - LHS and RHS strings of length between 1 and max_len (inclusive)
      - remove rules with LHS == RHS
      - if require_expanding is True: require |LHS| < |RHS|
    Yields:
      - rewriting system as a [lhs, rhs] pair."""
    for lhs in lazy_all_bin_upto_length(max_len_LHS):
        for rhs in substrings_upto_length(CS[0], max_len_RHS):
            if lhs == rhs:continue
            if require_expanding and len(lhs) >= len(rhs):
                continue
            yield rule(lhs, rhs)
def apply_rules(x, CS, max_len, max_backward_steps, max_res_size):
    # CS = current string [currS, sys, l], x = original input string
    # returns list of [res, newsys, complexity], sorted by complexity,
    # where res = backward rewriting from CS using newsys 
    # and newsys = sys + any new rule rnew 
    currS,sys,l = CS; maxFwd = max_backward_steps*2
    best_res_list = []
    for rnew in enumerate_rules(x, CS, max_len, require_expanding=True):
        newsys = sys.copy() if sys is not None else None
        if newsys is not None and rnew in newsys:
            continue
        if newsys is not None:
            newsys.insert(0, rnew)
        else:
            newsys = [rnew]
        forwardS, _, term = apply_forward_rewriting(currS, newsys, maxFwd)
        if forwardS != x or not term:
            continue
        res, steps, ok = apply_backward_rewriting(x, currS, newsys, max_backward_steps)
        if not ok: continue
        compNewsys = rsComplexity(newsys)
        if len(best_res_list) < max_res_size:
            best_res_list.append([res, newsys, len(res) + compNewsys])
        else:
            if len(res)+compNewsys < max(best_res_list, key=lambda x: x[2])[2]: 
                best_res_list.remove(max(best_res_list, key=lambda x: x[2]))
                best_res_list.append([res,newsys,len(res)+compNewsys])
    return sorted(best_res_list, key=lambda x: x[2], reverse=False)
#--- main backward generation compression function ---
def backGenCompress(x):
    dummyRS = None; LS = [[x, dummyRS, len(x)]]; i = 0
    DONE = []
    while True: # keep adding solutions to LS
        if len(LS) > maxLSsize:
            print("Termination condition 2: len(LS) > maxLSsize")
            break
        if len(LS) == 0:
            print("No compression found")
            return x, None, len(x)  
        CS = LS[0]; # get best current string
        DONE.append(LS[0]); LS = LS[1:]  # remove it from LS
        best_res_list = apply_rules(x, CS, max_len, max_backward_steps, max_res_size)
        if best_res_list: 
            LS.extend(best_res_list)
            LS = sorted(LS, key=lambda y: y[2], reverse=False)
        i += 1
    #join DONE and LS
    LS.extend(DONE) # then sort LS and select best result neq x
    bestR = [res for res in LS if res[0] != x]
    bestR = sorted(bestR, key=lambda x: x[2], reverse=False)
    selected = bestR[0]
    return selected[0], selected[1], selected[2]
# process potentially random string x
def process(x):
    resX,sys,compl = backGenCompress(x)
    if sys is None:
        return None, None
    c,s,t = apply_forward_rewriting(resX,sys,100)
    forwardOK = (c == x and t)
    if forwardOK: 
        return(resX, sys) 
    else: 
        return(None, None)
def rsComplexity(rules): # custom complexity function
        #splice a bias for specific system sizes
        if len(rules) == 1:
            return rsPrefixFreeComplexity_expanding(rules)-0
        if len(rules) == 2: #prefer, encode first
            return rsPrefixFreeComplexity_expanding(rules)-0
        if len(rules) == 3:
            return rsPrefixFreeComplexity_expanding(rules)-0
        else:
            return rsPrefixFreeComplexity_expanding(rules)

#%% parameters and input reading, process all strings in xlist.txt
# Entry point for proof-of-principle execution
def main():
    # Read x from file, containing a list of strings, one per line
    with open("xlist.txt", "r") as f:
        xlist = f.read().strip().splitlines()
        if xlist:
            print(f"Read {len(xlist)} strings from xlist.txt")
            lenx = len(xlist[0])
            lenTP = math.ceil(lenx + 3 * math.log2(lenx) + 3)
            print(f"Length of first string: {lenx}, length of trivial solution: {lenTP}")
        else:
            raise ValueError("Input file x.txt is empty")
    start_time = datetime.now()
    print(f"Starting processing at {start_time}\n")
    results = []
    for x in xlist[0:maxLines]:
        resX,sys = process(x)
        if resX and sys:
            print(f"x    = {x}:")
            print(f"resX = {resX}")
            pretty_print_rs(sys)
            results.append((len(resX)+rsComplexity(sys), x, resX, sys))
            print(f"len(resX)+compl(sys) = {len(resX)} + {rsComplexity(sys)} = {len(resX)+rsComplexity(sys)}, randomness = {(len(resX)+rsComplexity(sys)) - lenTP}\n")
            if (len(resX)+rsComplexity(sys)) - lenTP < thrRandomness:
                print("ALARM: generated a string with randomness below threshold!\n")
        else:
            print(f"No valid compression found for x = {x}\n")
    end_time = datetime.now()
    print(f"Finished processing at {end_time}, duration {end_time - start_time}")

    # print summary of results
    print("\nSummary of results:")
    results = sorted(results, key=lambda y: y[0], reverse=False)
    for total_comp, x, resX, sys in results:
        print(f"x    = {x}:")
        print(f"resX = {resX}")
        print(f"length of x = {len(x)}, length of resX = {len(resX)}, difference = {len(x)-len(resX)}")
        pretty_print_rs(sys)
        print(f"complexity = len(resX)+compl(sys) = {len(resX)} + {rsComplexity(sys)} = {len(resX)+rsComplexity(sys)}, randomness = {(len(resX)+rsComplexity(sys)) - lenTP}\n")
    #print synthetic results to a file
    filename = "results_" + str(max_len_LHS) + "_" + str(max_len_RHS) + "_" + \
        str(max_backward_steps) + "_" + str(max_res_size) \
        + "_" + str(maxLSsize) + ".txt"
    with open(filename, "w") as f:
        for total_comp, x, resX, sys in results:
            f.write(f"x    = {x}:\n")
            f.write(f"resX = {resX}\n")
            f.write(f"length of x = {len(x)}, length of resX = {len(resX)}, difference = {len(x)-len(resX)}\n")
            f.write("Rewriting System:\n")
            for lhs, rhs in sys:
                f.write(f"  {lhs} -> {rhs}\n")
            f.write(f"complexity = len(resX)+compl(sys) = {len(resX)} + {rsComplexity(sys)} = {len(resX)+rsComplexity(sys)}, randomness = {(len(resX)+rsComplexity(sys)) - lenTP}\n\n")
    f.close()

    sfilename = "sum" + filename 
    with open(sfilename, "w") as f:
        f.write(f"Finished processing at {end_time}, duration {end_time - start_time}\n")
        f.write(f"length of strings: {len(x)}\n")
        f.write(f"len of trivial solution: {lenTP}\n")
        a = list(range(len(x) - 8, lenTP))
        counts = [0] * len(a)
        for r in results:
            randomness = lenTP - r[0]
            idx = int(r[0]) - 50
            if 0 <= randomness < len(counts):
                counts[randomness] += 1
        f.write(str(counts) + "\n")
        for i, c in enumerate(counts):
            f.write(f"Randomness -{i}\tlength {lenTP-i}\t{c} solutions\n")
    f.close()

if __name__ == "__main__":
    # Parameters
    max_len = 8 # max length of LHS and RHS in rules 
    max_len_LHS = 6 # max length of LHS and RHS in rules 
    max_len_RHS = 13 # max length of LHS and RHS in rules 
    max_backward_steps = 25 # max backward steps to explore
    max_res_size = 99  # max n. of rules applied backwards in one step
    maxLSsize = 100  # max size of LS (current strings to process)
    max_expansion = 1.2  # do not consider strings longer than len(x)*max_expansion
    maxLines = 15000 # max number of lines to process from xlist.txt
    thrRandomness = -13 # threshold for randomness alarm
    main()
