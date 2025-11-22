from reo import *

sync = Connector()
sync.connect('Sync', 'A', 'B')

lossy = Connector()
lossy.connect('LossySync', 'A', 'B')

result, counterexample, smt = lossy.isRefinementOf(sync, 10)

print(result)
print(counterexample)
