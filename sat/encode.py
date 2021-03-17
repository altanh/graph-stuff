"""
Encode a SAT instance as a graph.
"""
import graph_tool.all as gt
import pysat
import scipy
import numpy as np
import matplotlib.pyplot as plt

from pysat.formula import CNF


def cnf_lit_to_index(lit: int, nv: int):
    if lit < 0:
        return nv - lit - 1
    return lit - 1


def neurosat_encoding(cnf: CNF, connect_literals=False):
    ug = gt.Graph(directed=False)
    node_type = ug.new_vertex_property("string")
    edge_type = ug.new_edge_property("string")
    ug.vp.node_type = node_type
    ug.ep.edge_type = edge_type

    literals = list(ug.add_vertex(2 * cnf.nv))
    clauses = list(ug.add_vertex(len(cnf.clauses)))

    # node types
    for lit_node in literals:
        node_type[lit_node] = "blue"
    for clause_node in clauses:
        node_type[clause_node] = "orange"

    # connect literals to clauses
    for i, clause in enumerate(cnf.clauses):
        for lit in clause:
            e = ug.add_edge(clauses[i], literals[cnf_lit_to_index(lit, cnf.nv)])
            edge_type[e] = "black"

    if connect_literals:
        for i in range(cnf.nv):
            e = ug.add_edge(literals[i], literals[cnf.nv + i])
            edge_type[e] = "blue"

    return ug


def polar_var_encoding(cnf: CNF):
    ug = gt.Graph(directed=False)
    node_type = ug.new_vertex_property("string")
    edge_type = ug.new_edge_property("string")
    ug.vp.node_type = node_type
    ug.ep.edge_type = edge_type

    literals = list(ug.add_vertex(cnf.nv))
    clauses = list(ug.add_vertex(len(cnf.clauses)))

    # node types
    for lit_node in literals:
        node_type[lit_node] = "blue"
    for clause_node in clauses:
        node_type[clause_node] = "orange"

    # connect literals to clauses
    for i, clause in enumerate(cnf.clauses):
        for lit in clause:
            e = ug.add_edge(clauses[i], literals[abs(lit) - 1])
            edge_type[e] = "green" if lit > 0 else "red"

    return ug
