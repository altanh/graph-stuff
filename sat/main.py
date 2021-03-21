import graph_tool.all as gt
import pysat
import scipy
import numpy as np
import matplotlib.pyplot as plt
import itertools
import pandas as pd

import pysat.solvers
from pysat.formula import CNF

import encode
import analyze


INSTANCES = [
    "./local/sat/chu-min-li/matrix/Mat26.shuffled.cnf",
    "./local/sat/goldberg/bmc2/cnt07.shuffled.cnf",
    "./local/sat/simon/satex-challenges/par32-5-c.shuffled.cnf",
    "./local/sat/goldberg/fpga_routing/apex7_gr_2pin_w4.shuffled.cnf",
    "./local/sat/biere/cmpadd/ca032.shuffled.cnf",
    "./local/sat/chu-min-li/urquhart/urquhart4_25.shuffled.cnf",
    "./local/sat/pehoushek/ezfact/ezfact16_1.shuffled.cnf",
    "./local/sat/biere/dinphil/dp05s05.shuffled.cnf",
    "./local/sat/goldberg/hanoi/hanoi4.shuffled.cnf",
    "./local/sat/ricci-tersenghi/glassy-sat-sel/glassy-sat-sel_N210_n.shuffled.cnf",
    "./local/sat/goldberg/bmc1/61.shuffled.cnf",
    "./local/sat/prestwich/mediator/med11.shuffled.cnf",
    "./local/sat/simon/satex-challenges/c3540-s.shuffled.cnf",
    "./local/sat/aloul/Bart/bart30.shuffled.cnf",
    "./local/sat/vangelder/RopeBench/rope_0050.shuffled.cnf",
    "./local/sat/dellacherie/comb/comb1.shuffled.cnf",
    "./local/sat/pehoushek/graphcolors3/3col120_5_4.shuffled.cnf",
    "./local/sat/pehoushek/plainoldcnf/5cnf_4000_4000_60t5.shuffled.cnf",
]


def run(cnf: CNF):
    with pysat.solvers.Minisat22(bootstrap_with=cnf.clauses) as solver:
        if solver.solve():
            print("SAT")
        else:
            print("UNSAT")


def render_spectral_2d(enc: gt.Graph, output: str, norm=True):
    pos = analyze.spectral_immersion(enc, n=2, norm=norm)
    gt.graph_draw(
        enc,
        pos=pos,
        vertex_fill_color=enc.vp.node_type,
        edge_color=enc.ep.edge_type,
        output=output,
    )


def plot_spectral_3d(enc: gt.Graph, norm=True):
    pos = analyze.spectral_immersion(enc, n=3, norm=norm, raw_array=True)
    ax = plt.subplot(111, projection="3d")

    # vertices
    cs = [enc.vp.node_type[v] for v in enc.vertices()]
    ax.scatter(pos[:, 0], pos[:, 1], pos[:, 2], c=cs, alpha=0.9)

    # edges
    for e in enc.edges():
        ps = [[], [], []]
        for v in [e.source(), e.target()]:
            for i in range(3):
                ps[i].append(pos[enc.vertex_index[v], i])
        ax.plot(ps[0], ps[1], ps[2], c=enc.ep.edge_type[e], alpha=0.6)

    plt.show()


if __name__ == "__main__":
    output_dir = "renders/spectral_sat"

    encodings = ["polar_var", "var_incidence"]
    norms = ["unnorm", "norm"]

    cheeger = []
    for encoding in encodings:
        print("-- running with encoding={}".format(encoding))
        for instance in INSTANCES:
            problem_name = instance.split("/")[-1].split(".cnf")[0]

            print("-- processing instance \"{}\"...".format(instance))
            cnf = CNF(from_file=instance)
            ug = encode.ENCODINGS[encoding](cnf)
            print("encoding has {} vertices, {} edges.".format(ug.num_vertices(), ug.num_edges()))

            ug_c = gt.extract_largest_component(ug, prune=True)
            if ug_c.num_vertices() < ug.num_vertices():
                print(
                    f'problem "{problem_name}" has multiple connected components, proceeding with largest...'
                )

            lb, ub = analyze.cheeger(ug_c)
            print("got Cheeger bound: {} <= h_G <= {}".format(lb, ub))
            cheeger.append({
                "problem": problem_name,
                "encoding": encoding,
                "cheeger_lb": lb,
                "cheeger_ub": ub,
            })

            for norm in norms:
                render_file = f"{output_dir}/{problem_name}.{encoding}.{norm}.pdf"
                print("rendering with {} Laplacian...".format(norm))
                render_spectral_2d(ug_c, render_file, norm=(norm == "norm"))
            # plot_spectral_3d(ug_c, norm=True)
    df = pd.DataFrame(cheeger)
    df.to_csv(output_dir + "/cheeger.csv")
