"""
Analyze a graph encoding of a SAT instance.
"""
import graph_tool.all as gt
import pysat
import scipy
import numpy as np
import matplotlib.pyplot as plt


# use normalized Laplacian for general (irregular) graphs
# http://www.math.ucsd.edu/~fan/wp/cheeger.pdf
def cheeger(enc: gt.Graph):
    L = gt.laplacian(enc, norm=True, operator=False)
    ls = scipy.sparse.linalg.eigsh(
        L, k=2, sigma=0, which="LM", return_eigenvectors=False
    )
    l2 = ls[1]
    return (l2 / 2, np.sqrt(2 * l2))


def spectral_immersion(enc: gt.Graph, n=2, norm=True, raw_array=False):
    """Immerse in vertices in R^n using the eigenvectors of the Laplacian"""
    L = gt.laplacian(enc, norm=norm, operator=False)
    _, vs = scipy.sparse.linalg.eigsh(
        L, k=n+1, sigma=0, which="LM", return_eigenvectors=True
    )
    immersion = vs[:, 1:]
    if raw_array:
        return immersion

    pos = enc.new_vertex_property("vector<double>")
    for v in enc.vertices():
        pos[v] = immersion[enc.vertex_index[v]]
    return pos
