from z3 import *

def Conjunction(constraints):
    assert len(constraints) > 0

    result = None
    for c in constraints:
        if result is None:
            result = c
        else:
            result = And(result, c)

    return result


def Disjunction(constraints):
    assert len(constraints) > 0

    result = None
    for c in constraints:
        if result is None:
            result = c
        else:
            result = Or(result, c)
    return result


class Channel:
    @staticmethod
    def Sync(nodes, bound):
        '''
        Sync(synchronous channel): one source end and one sink end.
        The pair of I/O operations on its two ends can only succeed simultaneously.
        :param bound: The maximum number of operations to be processed at both ends of the channel.
        '''
        assert len(nodes) == 2
        constraints = []
        for i in range(bound):
            constraints += [ nodes[0]['data'][i] == nodes[1]['data'][i] ]  # Same data
            constraints += [ nodes[0]['time'][i] == nodes[1]['time'][i] ]  # Simultaneously

        return Conjunction(constraints)

    @staticmethod
    def Fifo1(nodes, bound):
        '''
        FIFOn(asynchronous channel): one source end and one sink end, a bounded buffer with capacity n.
        It can accept ndata items from its source end before emitting data on its sink end.
        The accepted data items are kept in the internal buffer, and dispensed to the sink end in FIFO order.
        Especially, the FIFO1 channel is an instance of FIFOn where the buffer capacity is 1.
        '''
        assert len(nodes) == 2
        constraints = []
        for i in range(bound):
            constraints += [ nodes[0]['data'][i] == nodes[1]['data'][i] ]  # Same data
            constraints += [ nodes[0]['time'][i] <  nodes[1]['time'][i] ]  # Asynchronous: send first, then receive
            if i != 0:
                # Buffer capacity 1: The next transmission must occur after the current reception is complete.
                constraints += [ nodes[0]['time'][i] > nodes[1]['time'][i-1] ]

        return Conjunction(constraints)

    @staticmethod
    def Fifo1e(e):
        def Fifo1eInstance(nodes, bound):
            '''
            Return a function that generates an instance of Fifo1e channel (specific variant FIFO channel).
            There is a data e in the initial buffer-e needed to be the first data transformed.
            '''
            assert len(nodes) == 2
            constraints = []
            constraints += [nodes[1]['data'][0] == 1]  # The first data of the sink end is fixed at 1.
            for i in range(bound-1):
                constraints += [nodes[0]['data'][i] == nodes[1]['data'][i + 1]]  # Data delay in transmission
                constraints += [nodes[0]['time'][i] < nodes[1]['time'][i + 1]]  # Delayed reception
            for i in range(bound):
                constraints += [nodes[0]['time'][i] > nodes[1]['time'][i]]

            return Conjunction(constraints)
        return Fifo1eInstance
        
    @staticmethod
    def SyncDrain(nodes, bound):
        '''
        SyncDrain(synchronous channel): two source ends.
        The pair of input operations on its two ends can only succeed simultaneously.
        All data items written to this channel are lost.
        '''
        assert len(nodes) == 2
        constraints = []
        for i in range(bound):
            constraints += [nodes[0]['time'][i] == nodes[1]['time'][i]]  # No data constraints-lost.

        return Conjunction(constraints)
    
    @staticmethod
    def LossySync(nodes, bound, idx = 0, num = 0):
        '''
        LossySync(synchronous channel): one source end and one sink end.
        The source end always accepts all data items.
        If there is no matching output operation on the sink end of the channel at the time that a data item is accepted,
        then the data item is lost; otherwise, the channel transfers the data item as a Sync channel,
        and the output operation at the sink end succeeds.
        '''
        assert len(nodes) == 2
        # Termination condition: If the sink side has processed all data (num=bound),
        # or the source side has no more data (idx=bound), return true (constraint satisfied).
        if bound == num:
            return True
        if bound == idx:
            return True
        constraints_0 = []
        constraints_1 = []
        # constraints_0: The idx-th data at the source end is lost (time mismatch, source end advancing the index).
        constraints_0 += [ nodes[0]['time'][idx] != nodes[1]['time'][num]]
        # Constraint 2: The idx-th data from the source has been successfully transmitted (data and time match,
        # both sides advance the index)
        constraints_1 += [ nodes[0]['data'][idx] == nodes[1]['data'][num]]
        constraints_1 += [ nodes[0]['time'][idx] == nodes[1]['time'][num]]
        # Disjunction of two cases (logical OR): either data loss or successful transmission.
        return Or(And(Conjunction(constraints_0), Channel.LossySync(nodes, bound, idx + 1, num)),
                  And(Conjunction(constraints_1), Channel.LossySync(nodes, bound, idx + 1, num + 1)))

    @staticmethod
    def Producerp(p):  # p is a list
        def ProducerpInstance(nodes, bound):
            assert len(nodes) == 2
            constraints = []
            for i in range(bound):
                constraints += [Disjunction([nodes[1]['data'][i] == v for v in p])]
                constraints += [nodes[0]['time'][i] == nodes[1]['time'][i]]
            return Conjunction(constraints)

        return ProducerpInstance

    @staticmethod
    def AsynSpout(nodes, bound):  # DIY
        # two nodes are both sinks
        def Asyn(a, b, i=0, j=0):
            if i == bound or j == bound:
                return True
            if a[i] < b[j]:
                return And(a[i] != b[j], Asyn(a, b, i + 1, j))
            else:
                return And(a[i] != b[j], Asyn(a, b, i, j + 1))

        assert len(nodes) == 2
        constraints = []
        constraints += [len(nodes[0]['time']) == len(nodes[1]['time'])]
        constraints += [Asyn(nodes[0]['time'], nodes[1]['time'])]
        return Conjunction(constraints)

    @staticmethod
    def AsynDrain(nodes, bound):  # DIY
        # two nodes are both sources
        def Asyn(a, b, i=0, j=0):
            if i == bound or j == bound:
                return True
            if a[i] < b[j]:
                return And(a[i] != b[j], Asyn(a, b, i + 1, j))
            else:
                return And(a[i] != b[j], Asyn(a, b, i, j + 1))

        assert len(nodes) == 2
        constraints = []
        constraints += [len(nodes[0]['time']) == len(nodes[1]['time'])]
        constraints += [Asyn(nodes[0]['time'], nodes[1]['time'])]
        return Conjunction(constraints)

    @staticmethod
    def SyncSpout(nodes, bound):  # DIY
        # two nodes are both sinks
        assert len(nodes) == 2
        constraints = []
        for i in range(bound):
            constraints += [nodes[0]['time'][i] == nodes[1]['time'][i]]
        return Conjunction(constraints)

    @staticmethod
    def Merger(nodes, bound, idx_1 = 0, idx_2 = 0):
        '''
        Two source ends and one merged sink end.
        Merge data from two sources in chronological order into a single sink.
        '''
        assert len(nodes) == 3
        # Termination condition: The total number of operations at both source ends reaches the bound
        # (merging completed), return true.
        if bound == idx_1 + idx_2:
            return True
        constraints_1 = []
        constraints_2 = []
        # Constraints1: Retrieve data from the first source.
        constraints_1 += [ nodes[0]['data'][idx_1] == nodes[2]['data'][idx_1 + idx_2]]  # Same data
        constraints_1 += [ nodes[0]['time'][idx_1] == nodes[2]['time'][idx_1 + idx_2]]  # Time match
        constraints_1 += [ nodes[0]['time'][idx_1] <  nodes[1]['time'][idx_2]]  # 1 operation is earlier than 2.
        # Constraints2: Retrieve data from the second source.
        constraints_2 += [ nodes[1]['data'][idx_2] == nodes[2]['data'][idx_1 + idx_2]]  # Same data
        constraints_2 += [ nodes[1]['time'][idx_2] == nodes[2]['time'][idx_1 + idx_2]]  # Time match
        constraints_2 += [ nodes[1]['time'][idx_2] <  nodes[0]['time'][idx_1]]  # 2 operation is earlier than 1.
        return Or(And(Conjunction(constraints_1), Channel.Merger(nodes, bound, idx_1 + 1, idx_2)),
                  And(Conjunction(constraints_2), Channel.Merger(nodes, bound, idx_1, idx_2 + 1)))

    @staticmethod
    def Replicator(nodes, bound):  # DIY 0 --> 1, 2
        assert len(nodes) == 3
        constraints = []
        for i in range(bound):
            constraints += [nodes[0]['data'][i] == nodes[1]['data'][i]]
            constraints += [nodes[0]['time'][i] == nodes[1]['time'][i]]
            constraints += [nodes[0]['data'][i] == nodes[2]['data'][i]]
            constraints += [nodes[0]['time'][i] == nodes[2]['time'][i]]
        return Conjunction(constraints)

    @staticmethod
    def FlowThrough(nodes, bound):  # DIY 0 --> _ --> 2
        assert len(nodes) == 2
        constraints = []
        for i in range(bound):
            constraints += [nodes[0]['data'][i] == nodes[1]['data'][i]]
            constraints += [nodes[0]['time'][i] == nodes[1]['time'][i]]
        return Conjunction(constraints)