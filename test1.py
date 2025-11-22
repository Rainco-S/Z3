from reo import *

sync = Connector()
sync.connect('Sync', 'A', 'B')

fifo1 = Connector()
fifo1.connect('Fifo1', 'A', 'B')

result, counterexample, smt = fifo1.isRefinementOf(sync, 10)

print(result)
print(counterexample)
