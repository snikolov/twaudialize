import math
import pickle
import random
import sys
import time

from collections import defaultdict
from OSC import OSCClient, OSCMessage
from signal import *

from util import to_scale, neighbors_k

DEBUG = False

id = sys.argv[1]
instrument_len_scale = float(sys.argv[2])
instrument_start_note = int(sys.argv[3])
instrument_note_resolution = float(sys.argv[4])

if len(sys.argv) == 6:
  seed = sys.argv[5]
else:
  seed = random.randint(0, 100000000)
print 'seed', seed
random.seed(seed)

# topic_to_edges = pickle.load(open('../data/meme_edges.pkl'))

# edges = topic_to_edges['BigTimeRushZFestival']
edges = pickle.load(open('../data/edges_FollowBackATwitterosChilenos.pkl'))
#edges = pickle.load(open('../data/edges_TurkishDirectionersLovesHarryStayStrong.pkl'))

# Build adjacency list.
adj = defaultdict(list)

DIRECTED = True
JUMPS = False

# For now, work with a static graph. Ignore timestamps.  
# WARNING: Note that src and dst in edges are with respect to the follow graph,
# not the direction of information spreading.
for (dst, src, timestamp) in edges:
  adj[src].append(dst)
  if DIRECTED:
    adj[dst].append(src)

# Simulate walkers.
NUM_TIME_STEPS = 100000

client = OSCClient()
client.connect(("localhost", 7110))
oscMsg = OSCMessage('/midi/' + str(id))
oscMsg.append(0)

curr = adj.keys()[random.randint(0, len(adj) - 1)]

for i in xrange(NUM_TIME_STEPS):
  if DEBUG:
    print curr
  if curr not in adj or (i % 32 == 0 and random.random() < 0.50) and JUMPS:
    # Jump to a random node.
    curr = adj.keys()[random.randint(0, len(adj) - 1)]
    if DEBUG:
      print 'Jumping to', curr
  neighbors = adj[curr]
  neighborhood_size = len(neighbors_k(adj, curr, 2))
  midi_note = neighborhood_size // 2 + instrument_start_note
  if DEBUG:
    print "neighbors: ", neighborhood_size, midi_note
  time.sleep(instrument_note_resolution * math.ceil(instrument_len_scale / (1 + math.log(len(neighbors), 10)) / instrument_note_resolution))

  #neighbors.append(curr)

  curr = neighbors[random.randint(0, len(neighbors) - 1)]
  # print seed, midi_note

  # Map to pentatonic scale.
  midi_note = to_scale([0, 2, 4, 7, 9], midi_note)
  if midi_note > 127:
    print "can't hear", midi_note
  oscMsg[0] = midi_note

  client.send(oscMsg)
  

