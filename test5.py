from reo import *

c1 = Connector()

c1.connect('LossySync'   , 'A', 'B')
c1.connect('LossySync'   , 'A', 'D')
c1.connect('SyncDrain', 'A', 'C')
c1.connect('Sync'     , 'B', 'B1')
c1.connect('Sync'     , 'D', 'D1')
c1.connect('Merger'   , 'B1', 'D1', 'C')
c1.connect('Sync'     , 'B', 'E')
c1.connect('Sync'     , 'D', 'F')

c2 = Connector()

c2.connect('Sync'     , 'A', 'B')
c2.connect('LossySync'   , 'A', 'D')
c2.connect('SyncDrain', 'A', 'C')
c2.connect('Sync'     , 'B', 'B1')
c2.connect('Sync'     , 'D', 'D1')
c2.connect('Merger'   , 'B1', 'D1', 'C')
c2.connect('Merger'   , 'D', 'E', 'F')
c2.connect('Sync'     , 'B', 'E')
c2.connect('Sync'     , 'D', 'F')

result1, counterexample1, smt1 = c2.isRefinementOf(c1, 10)
result2, counterexample2, smt2 = c1.isRefinementOf(c2, 10)

print(result1)
print(result2)
print(counterexample1)
print(counterexample2)