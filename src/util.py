from scipy import sparse

def to_scale(pattern, midi_note, interval = 12):
  base = interval * (midi_note // interval)
  remainder = midi_note - base
  diffs = [ (abs(pattern[i] - remainder), i) for i in range(len(pattern)) ]
  diffs.sort()
  return base + pattern[diffs[0][1]]  

def neighbors_k(adj, src, k):
  ret = []
  visited = []
  to_visit = [(src, 0)]
  while len(to_visit) > 0:
    node = to_visit[0]
    to_visit.remove(node)
    if node[1] > k:
      break
    if node[0] not in visited:
      visited.append(node[0])
    else:
      continue
    ret.append(node[0])
    to_visit.extend([ (n, node[1] + 1) for n in adj[node[0]] ])

  return ret


  for src in adj:
    for dst in adj[src]:
      di = idx[dst]
      if src == '-1':
        # Self loop to trick conn comp into detecting a separate component.
        mat[(di,di)] = 1
      else:
        si = idx[src]
        mat[(si, di)] = 1
  return mat, idx, ridx
