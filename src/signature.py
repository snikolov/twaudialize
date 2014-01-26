import numpy as np

class Signature:
  def __init__(self, pattern, base = 45):
    self.pattern = pattern
    self.base = base

  @classmethod
  def from_nzpos(cls, value = 1, size = None, nzpos = None, base = None):
    assert(nzpos and len(nzpos) > 0)
    pattern = np.array([0] * size)
    pattern[np.array(nzpos)] = value
    return cls(pattern, base = base)

  @classmethod
  def from_nzprob(cls, value = 1, size = None, nzprob = None, base = None):
    keep = np.random.randint(0, 2, (size, 1))
    nzpos = [ i for i in range(len(keep)) if keep[i] == 1]
    if len(nzpos) == 0:
      nzpos = [ np.random.randint(0, size) ]
    return cls.from_nzpos(
      value = value,
      size = size,
      nzpos = nzpos,
      base = base)
  
  @classmethod
  def from_sum(cls, sigs):
    assert(sigs and len(sigs) > 0)
    pattern = np.copy(sigs[0].pattern)
    for sig in sigs[1:]:
      if np.random.random() < 0.125:
        pattern |= sig.pattern
    return cls(pattern)

  @classmethod
  def perturb(cls, sig, max_step = 1):
    pattern = np.copy(sig.pattern)
    nz = np.nonzero(pattern)[0]
    to_move_src = nz[np.random.randint(0, len(nz))]
    to_move_dst = \
      (to_move_src + np.random.randint(-max_step, max_step + 1)) % len(pattern)
    tmp = pattern[to_move_src]
    pattern[to_move_src] = 0
    pattern[to_move_dst] = tmp
    return cls(pattern)

  @classmethod
  def from_adj(cls, node, adj, sigs):
    parents = adj[node]

    """
    # Subsample parents
    keep = np.random.random((len(parents), 1)) < 0.25
    new_parents = [ parents[i] for i in range(len(keep)) if keep[i]]
    if len(new_parents) > 0:
      parents = new_parents
    """

    parent_sigs = [ sigs[parent] for parent in parents ]
    sigs_to_sum = []
    for parent_sig in parent_sigs:
      print 'perturbed', parent_sig.pattern
      perturbed = cls.perturb(parent_sig)
      print 'to', perturbed.pattern
      sigs_to_sum.append(perturbed)
    result = cls.from_sum(sigs_to_sum)
    print 'result:', result.pattern
    return result
