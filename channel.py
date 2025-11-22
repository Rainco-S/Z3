from z3 import *
from random import *

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
    # Special data
    CORRUPTED = 10
    TIMEOUT = 11
    OFF = 12
    RESET = 13
    EXPIRE = 14


    # basic channels in [9]
    @staticmethod
    def Sync(nodes, bound):
        assert len(nodes) == 2
        constraints = []
        for i in range(bound):
            constraints += [ nodes[0]['data'][i] == nodes[1]['data'][i] ]  # Same data
            constraints += [ nodes[0]['time'][i] == nodes[1]['time'][i] ]  # Simultaneously

        return Conjunction(constraints)

    @staticmethod
    def Fifo1(nodes, bound):
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
    def Fifon(n): # DIY
        def FifonInstance(nodes, bound):
            assert len(nodes) == 2
            constraints = []
            for i in range(bound):
                constraints += [nodes[0]['data'][i] == nodes[1]['data'][i]]
                constraints += [nodes[0]['time'][i] < nodes[1]['time'][i]]
            if i >= 1:
                constraints += [nodes[1]['time'][i] > nodes[1]['time'][i - 1]] # FIFO
            if i >= n:
                constraints += [nodes[0]['time'][i] > nodes[1]['time'][i - n]] # buffer size n

            return Conjunction(constraints)
        return FifonInstance

    @staticmethod
    def Fifo1e(e):
        def Fifo1eInstance(nodes, bound):
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
    def Fifone(n, e): # DIY, e is a list of length <= n
        def FifoneInstance(nodes, bound):
            assert len(nodes) == 2
            assert len(e) <= n
            constraints = []
            if bound >= len(e):
                for i in range(len(e)):
                    constraints += [nodes[1]['data'][i] == e[i]]
                for i in range(bound - len(e)):
                    constraints += [nodes[0]['data'][i] == nodes[1]['data'][i + len(e)]]
                    constraints += [nodes[0]['time'][i] < nodes[1]['time'][i + len(e)]]
                for i in range(bound - len(e) + 1):
                    constraints += [nodes[1]['time'][i] > nodes[1]['time'][i + len(e) - 1]]
                for i in range(n - len(e), bound):
                    constraints += [nodes[0]['time'][i] > nodes[1]['time'][i + len(e) - n]]
            else:
                for i in range(bound):
                    constraints += [nodes[1]['data'][i] == e[i]]
                    if i >= 1:
                        constraints += [nodes[1]['time'][i] > nodes[1]['time'][i - 1]]

            return Conjunction(constraints)
        return FifoneInstance
    
    @staticmethod
    def SyncDrain(nodes, bound):
        assert len(nodes) == 2
        constraints = []
        for i in range(bound):
            constraints += [nodes[0]['time'][i] == nodes[1]['time'][i]]  # No data constraints-lost.

        return Conjunction(constraints)
    
    @staticmethod
    def LossySync(nodes, bound, idx = 0, num = 0):
        assert len(nodes) == 2
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


    # additional channels in [10]
    @staticmethod
    def Filterp(p): # DIY
        # is p a list or a function? I use list here
        def FilterpInstance(nodes, bound, i = 0, j = 0):
            assert len(nodes) == 2
            if i == bound:
                return True
            constraints = []
            if nodes[0]['data'][i] in p:
                constraints += [nodes[0]['data'][i] == nodes[1]['data'][j]]
                constraints += [nodes[0]['time'][i] == nodes[1]['time'][j]]
                return And(Conjunction(constraints), FilterpInstance(nodes, bound, i + 1, j + 1))
            else:
                return FilterpInstance(nodes, bound, i + 1, j)
        
        return FilterpInstance
    
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

    # Probabilistic
    @staticmethod
    def CptSync(p):
        def CptSyncInstance(nodes, bound):
            assert len(nodes) == 2
            assert 0 <= p <= 1
            constraints = []
    
            for i in range(bound):
                q = uniform(0, 1)
                constraints += [nodes[0]['time'][i] == nodes[1]['time'][i]]
    
                if q > p:
                    constraints.append(nodes[1]['data'][i] == nodes[0]['data'][i])
                else:
                    constraints.append(nodes[1]['data'][i] == Channel.CORRUPTED)
    
            return Conjunction(constraints)
        return CptSyncInstance

    @staticmethod
    def RdmSync(nodes, bound):
        assert len(nodes) == 2
        constraints = []

        for i in range(bound):
            p = randint(0, 1)
            constraints += [nodes[0]['time'][i] == nodes[1]['time'][i]]

            if p > 0.5:
                constraints.append(nodes[1]['data'][i] == 1)
            else:
                constraints.append(nodes[1]['data'][i] == 0)

        return Conjunction(constraints)

    @staticmethod
    def ProbLossy(p):
        def ProbLossyInstance(nodes, bound, idx=0, num=0):
            assert len(nodes) == 2
            assert 0 <= p <= 1
    
            q = uniform(0, 1)
            if bound == num or bound == idx:
                return True
    
            constraints_0 = []
            constraints_1 = []
    
            constraints_0 += [nodes[0]['time'][idx] != nodes[1]['time'][num]]
    
            constraints_1 += [nodes[0]['data'][idx] == nodes[1]['data'][num]]
            constraints_1 += [nodes[0]['time'][idx] == nodes[1]['time'][num]]
    
            time_mismatch = And(
                Conjunction(constraints_0),
                Channel.ProbLossy(nodes, p, bound, idx + 1, num)
            )
    
            loss_prob = And(
                Conjunction([nodes[0]['time'][idx] == nodes[1]['time'][num]]),
                Channel.ProbLossy(nodes, p, bound, idx + 1, num)
            )
    
            success = And(
                Conjunction(constraints_1),
                Channel.ProbLossy(nodes, p, bound, idx + 1, num + 1)
            )
    
            branch_time_match = Or(
                And(q <= p, loss_prob),
                And(q > p, success)
            )
    
            return Or(time_mismatch, branch_time_match)
        return ProbLossyInstance

    @staticmethod
    def FtyFIFO1(p):
        def FtyFIFO1Instance(nodes, bound):
            assert len(nodes) == 2
            assert 0 <= p <= 1
    
            r = 0
            constraints = []
            for i in range(bound):
                q = uniform(0, 1)
                constraints += [nodes[0]['time'][i] < nodes[1]['time'][i]]
                if r == 0:
                    if q > p:
                        r = 1
                        constraints += [nodes[0]['data'][i] == nodes[1]['data'][i]]
                else:
                    constraints += [nodes[0]['time'][i] > nodes[1]['time'][i - 1]]
                    if q <= p:
                        r = 0
                    else:
                        constraints += [nodes[0]['data'][i] == nodes[1]['data'][i]]
    
            return Conjunction(constraints)
        return FtyFIFO1Instance

    # Timer
    @staticmethod
    def Timert(t): # DIY
        def TimertInstance(nodes, bound):
            assert len(nodes) == 2
            constraints = []
            for i in range(bound):
                constraints += [nodes[1]['data'][i] == Channel.TIMEOUT]
                constraints += [nodes[0]['time'][i] + t == nodes[1]['time'][i]]
                if i < bound - 1:
                    constraints += [nodes[0]['time'][i + 1] >= nodes[1]['time'][i] + t]
            return Conjunction(constraints)
        return TimertInstance
    
    @staticmethod
    def OFFTimert(t): # DIY
        def OFFTimertInstance(nodes, bound, i = 0, j = 0):
            assert len(nodes) == 2
            if i >= bound:
                return True
            if j >= bound:
                return True
            constraints_0, constraints_1 = [], []

            constraints_0 += [nodes[0]['data'][i + 1] == Channel.OFF]
            constraints_0 += [nodes[0]['time'][i] + t > nodes[1]['time'][i + 1]]
            # 需要加 i < bound - 1吗？不加的话，如果i == bound - 1自动不满足data[i + 1] == Channel.OFF

            constraints_1 += [nodes[1]['data'][j] == Channel.TIMEOUT]
            constraints_1 += [nodes[1]['time'][j] == nodes[0]['time'][i] + t]
            constraints_1 += [Or(nodes[0]['time'][i] + t <= nodes[1]['time'][i + 1], i == bound - 1)]

            return Or(
                And(Conjunction(constraints_0), OFFTimertInstance(nodes, bound, i + 2, j)),
                And(Conjunction(constraints_1), OFFTimertInstance(nodes, bound, i + 1, j + 1))
            )
        return OFFTimertInstance
        
    @staticmethod
    def RSTTimert(t): # DIY
        def RSTTimertInstance(nodes, bound, i = 0, j = 0):
            assert len(nodes) == 2
            if i >= bound:
                return True
            if j >= bound:
                return True
            constraints_0, constraints_1 = [], []

            constraints_0 += [nodes[0]['data'][i + 1] == Channel.RESET]
            constraints_0 += [nodes[0]['time'][i] + t > nodes[1]['time'][i + 1]]

            constraints_1 += [nodes[1]['data'][j] == Channel.TIMEOUT]
            constraints_1 += [nodes[1]['time'][j] == nodes[0]['time'][i] + t]
            constraints_1 += [Or(nodes[0]['time'][i] + t <= nodes[1]['time'][i + 1], i == bound - 1)]

            return Or(
                And(Conjunction(constraints_0), RSTTimertInstance(nodes, bound, i + 1, j)),
                And(Conjunction(constraints_1), RSTTimertInstance(nodes, bound, i + 1, j + 1))
            )
        return RSTTimertInstance
    
    @staticmethod
    def EXPTimert(t): # DIY
        def EXPTimertInstance(nodes, bound, i = 0):
            assert len(nodes) == 2
            if i >= bound:
                return True
            constraints_0, constraints_1 = [], []

            constraints_0 += [nodes[0]['data'][i + 1] == Channel.EXPIRE]
            constraints_0 += [nodes[1]['data'][i] == Channel.TIMEOUT]
            constraints_0 += [nodes[0]['time'][i] + t > nodes[1]['time'][i + 1]]
            constraints_0 += [nodes[1]['time'][i] == nodes[0]['time'][i + 1]]

            constraints_1 += [nodes[1]['data'][i] == Channel.TIMEOUT]
            constraints_1 += [nodes[1]['time'][i] == nodes[0]['time'][i] + t]
            constraints_1 += [Or(nodes[0]['time'][i] + t <= nodes[1]['time'][i + 1], i == bound - 1)]

            return Or(
                And(Conjunction(constraints_0), EXPTimertInstance(nodes, bound, i + 1)),
                And(Conjunction(constraints_1), EXPTimertInstance(nodes, bound, i + 1))
            )
        return EXPTimertInstance
    

    # Merge, Replicate, Flow 
    # 我发现Replicate和Flow是完全无用的
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
    def MultiMerger(nodes, bound): # DIY
        assert len(nodes) >= 3
        def MultiMergerInstance(Index = [0 for _ in range(len(nodes) - 1)]):
            if bound == sum(Index):
                return True
            constraints = []
            for i in range(len(nodes) - 1):
                temp = []
                temp += [nodes[i]['data'][Index[i]] == nodes[-1]['data'][sum(Index)]]
                temp += [nodes[i]['time'][Index[i]] == nodes[-1]['time'][sum(Index)]]
                for j in range(len(nodes) - 1):
                    if j != i:
                        temp += [nodes[i]['time'][Index[i]] < nodes[j]['time'][Index[j]]]
                constraints += [temp]
            return Disjunction([And(Conjunction(constraints[i]), MultiMergerInstance(Index[:i] + [Index[i] + 1] + Index[i + 1:])) for i in range(len(nodes) - 1)])
        return MultiMergerInstance()

    # @staticmethod
    # def Replicator(nodes, bound):  # DIY 0 --> 1, 2
    #     assert len(nodes) == 3
    #     constraints = []
    #     for i in range(bound):
    #         constraints += [nodes[0]['data'][i] == nodes[1]['data'][i]]
    #         constraints += [nodes[0]['time'][i] == nodes[1]['time'][i]]
    #         constraints += [nodes[0]['data'][i] == nodes[2]['data'][i]]
    #         constraints += [nodes[0]['time'][i] == nodes[2]['time'][i]]
    #     return Conjunction(constraints)

    # @staticmethod
    # def FlowThrough(nodes, bound):  # DIY 0 --> _ --> 2
    #     assert len(nodes) == 2
    #     constraints = []
    #     for i in range(bound):
    #         constraints += [nodes[0]['data'][i] == nodes[1]['data'][i]]
    #         constraints += [nodes[0]['time'][i] == nodes[1]['time'][i]]


    #     return Conjunction(constraints)
