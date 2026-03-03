## RNDevalRepeat — Research Prototype

This repository contains a proof-of-principle Python implementation corresponding to a research publication.  
The code reflects the experimental setup described in the paper and is provided solely for research and evaluation purposes. It is not intended as a production-ready or optimized implementation.

## Requirements

* Python 3.10 or later  
* No external dependencies beyond the Python standard library  

## Input Format

Prepare a text file `xlist.txt` containing:

* One binary string per line  
* All strings of equal length `n`  
* Each bit represented as the character `0` or `1`  

## Configuration

Algorithm parameters are defined within `RNDevalRepeat.py`.  
Default parameter values correspond to the experimental configuration reported for `n = 64`.  
Parameters may be adjusted directly in the source file to reproduce alternative configurations.

## Execution

Run:
python3 RNDevalRepeat.py
Results are printed to standard output.  
A summary file is written to:
sumresults_params.txt


## License

This software is provided solely for research and evaluation purposes.  

Copying, modification, redistribution, sublicensing, or commercial use is not permitted without prior written permission from the copyright holder.  

See the LICENSE file for full terms.
