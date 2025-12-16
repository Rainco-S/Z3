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


# Time based cases
test_time_01 = (
    ['Fifo1 A C', 'Timert(1) A D', 'Fifo1 D E', 'SyncDrain C E', 'Sync C B'],
    ['Fifo1 A F', 'Timert(1) A G', 'SyncDrain F G', 'Sync F B']
)


# Mixed cases
test_mixed_01 = (
    ['RdmSync A E', 'Fifo1 E D', 'Timert(1) E C', 'SyncDrain D C', 'Sync D B'],
    ['Fifo1 A D', 'Timert(1) A C', 'SyncDrain D C', 'Sync D E', 'RdmSync E B']
)