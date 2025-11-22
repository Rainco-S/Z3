from reo import *

c1 = Connector()
c1.connect('Sync', 'A', 'E')
c1.connect('Fifo1', 'E', 'C')
c1.connect('Fifo1', 'E', 'D')


c2 = Connector()
c2.connect('Fifo1', 'A', 'B')
c2.connect('Sync', 'B', 'C')
c2.connect('Sync', 'B', 'D')

result, counterexample, smt = c2.isRefinementOf(c1, 10)

print(result)
