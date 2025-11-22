from reo import *

c1 = Connector()
c1.connect('Sync', 'A', 'E')
c1.connect('Fifo1', 'E', 'F')
c1.connect('Fifo1', 'E', 'G')
c1.connect('Sync', 'F', 'B')
c1.connect('Sync', 'G', 'C')
c1.connect('SyncDrain','F','G')

c2 = Connector()
c2.connect('Fifo1', 'A', 'D')
c2.connect('Sync', 'D', 'B')
c2.connect('Sync', 'D', 'C')

result1, counterexample1, smt1 = c2.isRefinementOf(c1, 10)
result2, counterexample2, smt2 = c1.isRefinementOf(c2, 10)

print(result1)
print(result2)
