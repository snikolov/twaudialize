import math
import os
import pickle
import sys
import time

import matplotlib.pyplot as plt
import networkx as nx


from scipy import real
from scipy import sparse
from OSC import OSCClient, OSCMessage

plt.ion()

# Initialize OSC client
client = OSCClient()
client.connect(("localhost", 65442))
oscMsg = OSCMessage('/midi/0')
oscMsg.append(0)
oscMsg.append(0)

pause_factor = 1.5

# Sonify the global topology of an evolving graph.  
# Strategy: compute the graph Laplacian as the graph evolves and map eigenvalues
# to frequencies.

dataset = 'AlianzaParaPataerleEseCuloAMarioSilva'

#edges = pickle.load(open('../data/edges_FollowBackATwitterosChilenos.pkl'))
edges = pickle.load(open(os.path.join('../data/edges_max_3_parents', dataset + '.pkl')))

# WARNING: Note that src and dst in edges are with respect to the follow graph,
# not the direction of information spreading.
# Sort by time ascending.
edges.sort(key = lambda x : x[2])

plt.figure()

G = nx.Graph()

for i, (src, dst, timestamp) in enumerate(edges[:-1]):
  print src, dst
  if int(src) == -1:
    # print 'Adding node', dst
    G.add_node(dst)
  else:
    # print 'Adding edge', src, dst
    G.add_edge(src, dst)

  plt.subplot(211)
  plt.hold(False)
  nx.draw(G)

  L = nx.linalg.laplacian_spectrum(G)
  topL = sorted(L, reverse = True)[:6]

  plt.subplot(212)
  plt.hold(False)
  plt.plot(topL)
  # print L

  midi_vel = 127
  print topL

  # Take the real part, as there may be small error complex parts
  topL = [ float(real(l)) for l in topL ]
  midi_note_func = lambda l : 7.5 * math.log(l * 30 + 1, 1.8)
  # Send note-on messages
  sys.stdout.write('notes: ')
  for l in topL:
    midi_note = midi_note_func(l)
    sys.stdout.write(str(midi_note) + ', ')
    if midi_note > 127:
      print 'Can\'t hear', midi_note

    oscMsg[0] = midi_note
    oscMsg[1] = midi_vel
    client.send(oscMsg)
  sys.stdout.write('\n')

  time_diff_seconds = (edges[i + 1][2] - edges[i][2]) / 1000.0
  print 'time_diff', time_diff_seconds
  time.sleep(time_diff_seconds / float(pause_factor))
  #time.sleep(pause_time_seconds)
  # Send note-off messages
  for l in topL:
    oscMsg[0] = midi_note_func(l)
    oscMsg[1] = 0
    client.send(oscMsg)
   
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
