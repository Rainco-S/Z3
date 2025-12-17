from reo import *

# Basic cases
test_basic_01 = (
    ['Sync A B'],
    ['Fifo1 A B']
)

test_basic_02 = (
    ['Sync A B'],
    ['LossySync A B']
)

test_basic_03 = (
    ['Sync A E', 'Fifo1 E C', 'Fifo1 E D'],
    ['Fifo1 A B', 'Sync B C', 'Sync B D']
)

test_basic_04 = (
    ['Sync A E', 'Fifo1 E F', 'Fifo1 E G', 'Sync F B', 'Sync G C', 'SyncDrain F G'],
    ['Fifo1 A D', 'Sync D B', 'Sync D C']
)

test_basic_05 = (
    ['Sync A D', 'Sync D E', 'Sync D F', 'Fifo1 E B', 'Fifo1 F C'],
    ['Sync A D', 'Sync D E', 'Sync D F', 'Fifo1 E G', 'Fifo1 F H', 'SyncDrain G H', 'Sync G B', 'Sync H C']
)

test_basic_06 = (
    ['LossySync A B', 'LossySync A D', 'SyncDrain A C', 'Sync B C', 'Sync D C', 'Merger B D C', 'Sync B E', 'Sync D F'],
    ['Sync A B', 'LossySync A D', 'SyncDrain A C', 'Sync B C', 'Sync D C', 'Merger B D C', 'Sync B E', 'Sync D F']
)

test_basic_07 = (
    ['Sync A D', 'Sync D C', 'Sync B E', 'Sync E C', 'Merger D E C', 'SyncDrain E G', 'SyncDrain D H', 'Fifo1e(1) F G', 'Fifo1 G H', 'Sync H F'],
    ['Sync A D', 'LossySync D C', 'Sync B E', 'LossySync E C', 'Merger D E C', 'SyncDrain E G', 'SyncDrain D H', 'Fifo1e(1) F G', 'Fifo1 G H', 'Sync H F']
)

test_basic_08 = (
    ['Sync A D', 'Sync D C', 'Sync B E', 'Sync E C', 'Merger D E C', 'SyncDrain E G', 'SyncDrain D H', 'Fifo1e(1) F G', 'Fifo1 G H', 'Sync H F'],
    ['SyncDrain A B', 'Fifo1 A C', 'Sync B C', 'Merger A B C']
)


# Timer based cases
test_time_01 = (
    ['Fifo1 A C', 'Timert(1) A D', 'Fifo1 D E', 'SyncDrain C E', 'Sync C B'],
    ['Fifo1 A F', 'Timert(1) A G', 'SyncDrain F G', 'Sync F B']
)

test_time_02 = (
    ['Sync A G', 'LossySync G E', 'LossySync G F', 'Sync E H', 'Sync F H', 'Merger E F H', 'SyncDrain G H', 'Sync E C', 'Sync F D', 'Timert(1) C B', 'Timert(1) D B'],
    ['Sync A G0', 'LossySync G0 E0', 'Sync E0 H0', 'SyncDrain G0 H0', 'Sync E0 C0', 'Timert(1) C0 B']    
)

test_time_03 = (
    ['Sync A C', 'Fifo1 C D', 'Sync C F', 'Timert(1) F G', 'LossySync G H', 'SyncDrain D H', 'LossySync D E', 'Sync E H', 'Merger E G H', 'Sync E B'],
    ['Sync A C0', 'Fifo1 C0 D0', 'Sync C0 F0', 'Timert(1) F0 G0', 'Sync G0 H0', 'SyncDrain D0 H0', 'Sync D0 E0', 'Sync E0 H0', 'Merger E0 G0 H0', 'Sync E0 B']
)


# Probability based cases
test_prob_01 = (
    ['RdmSync A E', 'Fifo1 E D', 'Timert(1) E C', 'SyncDrain D C', 'Sync D B'],
    ['Fifo1 A D', 'Timert(1) A C', 'SyncDrain D C', 'Sync D E', 'RdmSync E B']
)

test_prob_02 = (
    ['Fifo1 A C', 'RdmSync C B'],
    ['RdmSync A D', 'Fifo1 D B']
)

test_prob_03 = (
    ['Fifo1 A C', 'RdmSync C B'],
    ['Sync A D', 'Fifo1 D E', 'LossyFIFO1(0.5) D G', 'LossySync E H', 'SyncDrain G H', 'LossySync E F', 'Producerp([0]) F B', 'Producerp([1]) G B', 'Merger F G B']
)

test_prob_04 = (
    ['RdmSync A D', 'Filterp([0]) D E', 'Filterp([1]) D F', 'LossySync A G', 'LossySync A H', 'SyncDrain E G', 'SyncDrain F H', 'Sync G B', 'Sync H C'],
    ['ProbLossy(0.5) A B', 'ProbLossy(0.5) A C']
)