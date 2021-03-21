import graph_tool.all as gt
import pysat
import scipy
import numpy as np
import matplotlib.pyplot as plt

import pysat.solvers
from pysat.formula import CNF

from encode import polar_var_encoding
from analyze import cheeger


INSTANCES = [
    "./local/sat/chu-min-li/matrix/Mat26.shuffled.cnf",
    "./local/sat/goldberg/bmc2/cnt07.shuffled.cnf",
]


def run(cnf: CNF):
    with pysat.solvers.Minisat22(bootstrap_with=cnf.clauses) as solver:
        if solver.solve():
            print("SAT")
        else:
            print("UNSAT")


if __name__ == "__main__":
    instance = INSTANCES[0]
    cnf = CNF(from_file=instance)
    ug = polar_var_encoding(cnf)

    ug_c = gt.extract_largest_component(ug)
    if ug_c.num_vertices() < ug.num_vertices():
        print("instance graph has multiple connected components, proceeding with largest...")

    lb, ub = cheeger(ug_c)
    print("{} <= h_G <= {}".format(lb, ub))
