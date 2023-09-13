[![check](https://github.com/retospect/cmdrnafold/actions/workflows/check.yml/badge.svg)](https://github.com/retospect/cmdrnafold/actions/workflows/check.yml)
# cmdrnafold - a commandline wrapper library for viennaRNA

A very simple python wrapper around [ViennaRNA Fold](https://www.tbi.univie.ac.at/RNA/ViennaRNA/refman/man/RNAfold.html)

This is handy commandline wrapper if you can not get the proper [ViennaRNA package](https://pypi.org/project/ViennaRNA/) to run right. 

Currently it only provides one interface that is a kind of drop in replacement:

``` python
from cmdrnafold import RNA
# import RNA // Could not get ViennaRNA package to work

sequence = "CGCAGGGAUACCCGCG"

# create new fold_compound object
fc = RNA.fold_compound(sequence)

# compute minimum free energy (mfe) and corresponding structure
(ss, mfe) = fc.mfe()

# print output
print("{} [ {:6.2f} ]".format(ss, mfe))
```

This tool requires the [viennaRNA commandline tools](https://www.tbi.univie.ac.at/RNA/).
