#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
import pickle
import random
import sys
import time

from collections import defaultdict
from OSC import OSCClient, OSCMessage

from util import to_scale, neighbors_k

from signature import Signature

sys.path.append('/Users/snikolov/projects/twesearch/')

from processing import build_gexf

SPEED_MULT = 100

topic = 'Mention20PeopleYouLoveOnTwitter'
#edges = pickle.load(open('../data/edges_max_10_parents/FollowBackATwitterosChilenos.pkl'))
#edges = pickle.load(open('../data/edges_max_10_parents/Mention20PeopleYouLoveOnTwitter.pkl'))
edges = pickle.load(open('../data/edges_max_10_parents/' + topic + '.pkl'))

print len(edges)

# Build adjacency list.
adj = defaultdict(list)

client = OSCClient()
client.connect(("localhost", 65443))
oscMsg = OSCMessage('/midi/0')
oscMsg.append(0)
oscMsg.append(0)

birth_times = {}
# Sort the edges in ascending time order.
edges.sort(key = lambda x: x[2])
# WARNING: Note that src and dst in edges are with respect to the direction of
# information spreading. The directions of the edges in adj are the reverse of
# this and represent parent pointers.
signatures = {}
SIGNATURE_SIZE = 8
SIGNATURE_NZPROB = 0.1

QUANTIZE_TIME = False
TIME_QUANTUM_SECONDS = 0.0675

# Organize events by time and nodes born at each time in a 2-level dict.
events_by_time = defaultdict(lambda: defaultdict(list))
for (src, dst, timestamp) in edges:
  events_by_time[timestamp][dst].append(src)

events_by_time = sorted(
  [ (t, events_by_time[t]) for t in events_by_time ],
  key = lambda x: x[0])

TARGET_DURATION_MILLIS = 150000
duration = (events_by_time[-1][0] - events_by_time[0][0])

SPEED_MULT = duration / TARGET_DURATION_MILLIS
print 'speed mult', SPEED_MULT

SUSTAIN_SECONDS = 0.25

"""
neighbor_counts = []
import matplotlib.pyplot as plt
plt.ion()
plt.figure()
plt.hold(False)
"""

prev_timestamp = events_by_time[0][0]
prev_midi_notes = []

edges_with_fake_timestamps = []

for i, (timestamp, dst_to_srcs) in enumerate(events_by_time[1:]):
  #print 'events at', timestamp, ':', dst_to_srcs
  for dst in dst_to_srcs:
    adj[dst].extend(dst_to_srcs[dst])

  for dst in dst_to_srcs:
    neighbors = neighbors_k(adj, dst, 5)
    # print 'num neighbors', len(neighboxrs)
    
    """
    neighbor_counts.append(len(neighbors))
    if i % 20 == 0:
      plt.hist(neighbor_counts)
      plt.draw()
    """
    skip = False
    """
    if len(neighbors) < 25 and random.random() < 0.5:
      print 'skipping'
      skip = True
    """

    if i % 50 == 0:
      print i + 1, '/', len(events_by_time) + 1

    midi_note = 34 + 0.80 * math.log(len(neighbors), 1.08) #45 + len(neighbors) // 25.0 
    #midi_note = to_scale([0, 2, 4, 7, 9], midi_note)
    midi_note = to_scale([0, 2, 4, 7, 9, 11], midi_note)
    midi_note += random.random() * 0.1
    midi_vel = 40 #5 + min(58, 58 * (len(neighbors) / 800.0))  #64.0 * (1 - math.exp(-(len(neighbors))) / 0.5)
    prev_midi_notes.append(midi_note)

    # Send OSC messages.

    # Send current note.
    # print 'midi note', midi_note
    if midi_note > 127:
      print 'Can\'t hear', midi_note
    oscMsg[0] = midi_note
    oscMsg[1] = midi_vel
    if not skip:
      client.send(oscMsg)
    
    # Update graph to be visualized.
    fake_timestamp = time.time()
    for src in dst_to_srcs[dst]:
      edges_with_fake_timestamps.append((src, dst, fake_timestamp))

  # Sustain notes.
  time.sleep(SUSTAIN_SECONDS)

  # Turn off previous notes.
  for prev_midi_note in prev_midi_notes:
    oscMsg[0] = prev_midi_note
    oscMsg[1] = 0
    client.send(oscMsg)
  prev_midi_notes = []

  #print timestamp - prev_timestamp
  time_to_sleep = (timestamp - prev_timestamp) / 1000.0 / SPEED_MULT
  if QUANTIZE_TIME:
    time_to_sleep = \
      TIME_QUANTUM_SECONDS * math.ceil(time_to_sleep / TIME_QUANTUM_SECONDS)
  time.sleep(time_to_sleep)
  prev_timestamp = timestamp

  """
  if src == -1:
    signatures[dst] = Signature.from_nzprob(
      size = SIGNATURE_SIZE,
      nzprob = SIGNATURE_NZPROB)
  elif src not in signatures:
    signatures[src] = Signature.from_nzprob(
      size = SIGNATURE_SIZE,
      nzprob = SIGNATURE_NZPROB)
  else:
    signatures[dst] = Signature.from_adj(
      dst,
      adj,
      signatures)
  """

#build_gexf(edges_with_fake_timestamps, topic)
#print edges_with_fake_timestamps[-1][2] - edges_with_fake_timestamps[0][2], 'seconds'
