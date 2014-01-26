import pickle
import networkx as nx
import matplotlib.pyplot as plt

from scipy import sparse

plt.ion()

# Sonify the global topology of an evolving graph.  
# Strategy: compute the graph Laplacian as the graph evolves and map eigenvalues
# to frequencies.

edges = pickle.load(open('../data/edges_FollowBackATwitterosChilenos.pkl'))

# WARNING: Note that src and dst in edges are with respect to the follow graph,
# not the direction of information spreading.
# Sort by time ascending.
edges.sort(key = lambda x : x[2])

G = nx.Graph()
for (src, dst, timestamp) in edges:
  print src, dst
  if src != '-1':
    G.add_node(src)
  else:
    G.add_node(src)
    G.add_node(dst)
    G.add_edge(src, dst)
  nx.draw(G)
  M = nx.linalg.laplacian_matrix(G)
  L = nx.linalg.laplacian_spectrum(G)
  print L
  print M
  raw_input()

"""
nodes = set()
for (src, dst, timestamp) in edges:
  nodes.add(src)
  nodes.add(dst)
  print src, dst
  idx = { n : i for i, n in enumerate(nodes)  }
  G = sparse.dok_matrix((len(nodes), len(nodes)))
  si = idx[src]
  di = idx[dst]
  if src == '-1':
    G[(di, di)] = 1
  else:
    G[(si, di)] = 1
    G[(di, si)] = 1
  
  L = sparse.csgraph.laplacian(G)
  print L
  raw_input()
"""
