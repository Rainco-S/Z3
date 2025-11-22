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

    # Basic Connectors
    @staticmethod
    def Sync(nodes, bound):
        assert len(nodes) == 2
        constraints = []
        for i in range(bound):
            constraints += [nodes[0]['data'][i] == nodes[1]['data'][i]]
            constraints += [nodes[0]['time'][i] == nodes[1]['time'][i]]
        return Conjunction(constraints)
    
    @staticmethod
    def Fifo1(nodes, bound):
        assert len(nodes) == 2
        constraints = []
        for i in range(bound):
            constraints += [nodes[0]['data'][i] == nodes[1]['data'][i]]
            constraints += [nodes[0]['time'][i] < nodes[1]['time'][i]]
            if i >= 1:
                constraints += [nodes[0]['time'][i] > nodes[1]['time'][i-1]]
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
            constraints += [nodes[1]['data'][0] == e]
            for i in range(bound - 1):
                constraints += [nodes[0]['data'][i] == nodes[1]['data'][i + 1]]
                constraints += [nodes[0]['time'][i] < nodes[1]['time'][i + 1]]
                constraints += [nodes[0]['time'][i] > nodes[1]['time'][i]]
            constraints += [nodes[0]['time'][bound - 1] > nodes[1]['time'][bound - 1]]
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
    def LossySync(nodes, bound, i = 0, j = 0):
        assert len(nodes) == 2
        if i >= bound: # nodes[0] is full
            return True
        if j >= bound: # nodes[1] is full
            return True
        constraints_0, constraints_1 = [], []

        constraints_0 += [nodes[0]['time'][i] != nodes[1]['time'][j]] # drop
        constraints_1 += [nodes[0]['data'][i] == nodes[1]['data'][j]] # transmit
        constraints_1 += [nodes[0]['time'][i] == nodes[1]['time'][j]]
        
        return Or(
            And(Conjunction(constraints_0), Channel.LossySync(nodes, bound, i + 1, j)),
            And(Conjunction(constraints_1), Channel.LossySync(nodes, bound, i + 1, j + 1))
        )
    
    @staticmethod
    def Filterp(p): # DIY
        # is p a list or a function? I use list here
        def FilterpInstance(nodes, bound, i = 0, j = 0):
            assert len(nodes) == 2
            if i == bound:
                return True
            constraints = []
            if nodes[0]['data'][i] in range(p):
                constraints += [nodes[0]['data'][i] == nodes[1]['data'][j]]
                constraints += [nodes[0]['time'][i] == nodes[1]['time'][j]]
                return And(Conjunction(constraints), FilterpInstance(nodes, bound, i + 1, j + 1))
            else:
                return FilterpInstance(nodes, bound, i + 1, j)
        return FilterpInstance

    @staticmethod
    def Producerp(p): # DIY
        # p also a list here
        def ProducerpInstance(nodes, bound):
            assert len(nodes) == 2
            constraints = []
            for i in range(bound):
                constraints += [Disjunction([nodes[1]['data'][i] == v for v in range(p)])]
                constraints += [nodes[0]['time'][i] == nodes[1]['time'][i]]
            return Conjunction(constraints)
        return ProducerpInstance
    
    @staticmethod
    def SyncDrain(nodes, bound):
        assert len(nodes) == 2
        constraints = []
        for i in range(bound):
            constraints += [nodes[0]['time'][i] == nodes[1]['time'][i]]
        return Conjunction(constraints)
    
    @staticmethod
    def AsynSpout(nodes, bound): # DIY
        # two nodes are both sinks
        def Asyn(a, b, i = 0, j = 0):
            if i == bound or j == bound:
                return True
            return Or(
                And(a[i]<b[j], Asyn(a, b, i + 1, j)),
                And(a[i]>b[j], Asyn(a, b, i, j + 1))
            )
        
        assert len(nodes) == 2
        constraints = []
        constraints += [len(nodes[0]['time']) == len(nodes[1]['time'])]
        constraints += [Asyn(nodes[0]['time'], nodes[1]['time'])]
        return Conjunction(constraints)
    
    # not provided, maybe with problems
    @staticmethod
    def AsynDrain(nodes, bound): # DIY
        # two nodes are both sources
        def Asyn(a, b, i = 0, j = 0):
            if i == bound or j == bound:
                return True
            return Or(
                And(a[i]<b[j], Asyn(a, b, i + 1, j)),
                And(a[i]>b[j], Asyn(a, b, i, j + 1))
            )

        assert len(nodes) == 2
        constraints = []
        constraints += [len(nodes[0]['time']) == len(nodes[1]['time'])]
        constraints += [Asyn(nodes[0]['time'], nodes[1]['time'])]
        return Conjunction(constraints)
    
    # not provided, maybe with problems
    @staticmethod
    def SyncSpout(nodes, bound): # DIY
        # two nodes are both sinks
        assert len(nodes) == 2
        constraints = []
        for i in range(bound):
            constraints += [nodes[0]['time'][i] == nodes[1]['time'][i]]
        return Conjunction(constraints)
    

    # 注意：这里可能需要把'OFF'等特殊输入变成数，以适应Z3的类型

    # Timers

    @staticmethod
    def Timert(t): # DIY
        def TimertInstance(nodes, bound):
            assert len(nodes) == 2
            constraints = []
            for i in range(bound):
                constraints += [nodes[1]['data'][i] == 'TIMEOUT']
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

            constraints_0 += [nodes[0]['data'][i + 1] == 'OFF']
            constraints_0 += [nodes[0]['time'][i] + t > nodes[1]['time'][i + 1]]
            # 需要加 i < bound - 1吗？不加的话，如果i == bound - 1自动不满足data[i + 1] == 'OFF'

            constraints_1 += [nodes[1]['data'][j] == 'TIMEOUT']
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

            constraints_0 += [nodes[0]['data'][i + 1] == 'RESET']
            constraints_0 += [nodes[0]['time'][i] + t > nodes[1]['time'][i + 1]]

            constraints_1 += [nodes[1]['data'][j] == 'TIMEOUT']
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

            constraints_0 += [nodes[0]['data'][i + 1] == 'EXPIRE']
            constraints_0 += [nodes[1]['data'][i] == 'TIMEOUT']
            constraints_0 += [nodes[0]['time'][i] + t > nodes[1]['time'][i + 1]]
            constraints_0 += [nodes[1]['time'][i] == nodes[0]['time'][i + 1]]

            constraints_1 += [nodes[1]['data'][i] == 'TIMEOUT']
            constraints_1 += [nodes[1]['time'][i] == nodes[0]['time'][i] + t]
            constraints_1 += [Or(nodes[0]['time'][i] + t <= nodes[1]['time'][i + 1], i == bound - 1)]

            return Or(
                And(Conjunction(constraints_0), EXPTimertInstance(nodes, bound, i + 1)),
                And(Conjunction(constraints_1), EXPTimertInstance(nodes, bound, i + 1))
            )
        return EXPTimertInstance


    # 这里最大的问题是：Composing Connector内部是否与组件Connector交叠？按[9]的实现，没有交叠，但这就需要额外澄清组件的Source和Sink，十分冗杂
    # 以下按[9]的思路实现

    # 另外，是否需要实现多对1和1对多？后者比前者简单

    # Composing Connectors
    @staticmethod
    def Merger(nodes, bound, i = 0, j = 0): # 0, 1 --> 2
        assert len(nodes) == 3
        if bound == i + j:
            return True
        constraints_1, constraints_2 = [], []

        constraints_1 += [nodes[0]['data'][i] == nodes[2]['data'][i + j]]
        constraints_1 += [nodes[0]['time'][i] == nodes[2]['time'][i + j]]
        constraints_1 += [nodes[0]['time'][i] < nodes[1]['time'][j]]

        constraints_2 += [nodes[1]['data'][j] == nodes[2]['data'][i + j]]
        constraints_2 += [nodes[1]['time'][j] == nodes[2]['time'][i + j]]
        constraints_2 += [nodes[1]['time'][j] < nodes[0]['time'][i]]

        return Or(
            And(Conjunction(constraints_1), Channel.Merger(nodes, bound, i + 1, j)),
            And(Conjunction(constraints_2), Channel.Merger(nodes, bound, i, j + 1))
        )
    
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
    
    # Connectors below are not needed

    # @staticmethod
    # def Replicator(nodes, bound): # DIY 0 --> 1, 2
    #     assert len(nodes) == 3
    #     constraints = []
    #     for i in range(bound):
    #         constraints += [nodes[0]['data'][i] == nodes[1]['data'][i]]
    #         constraints += [nodes[0]['time'][i] == nodes[1]['time'][i]]
    #         constraints += [nodes[0]['data'][i] == nodes[2]['data'][i]]
    #         constraints += [nodes[0]['time'][i] == nodes[2]['time'][i]]
    #     return Conjunction(constraints)
    
    # @staticmethod
    # def MultiReplicator(nodes, bound): # DIY
    #     assert len(nodes) >= 3
    #     constraints = []
    #     for i in range(bound):
    #         for j in range(1, len(nodes)):
    #             constraints += [nodes[0]['data'][i] == nodes[j]['data'][i]]
    #             constraints += [nodes[0]['time'][i] == nodes[j]['time'][i]]
    #     return Conjunction(constraints)
    
    # @staticmethod
    # def FlowThrough(nodes, bound): # DIY 0 --> _ --> 2
    #     assert len(nodes) == 2
    #     constraints = []
    #     for i in range(bound):
    #         constraints += [nodes[0]['data'][i] == nodes[1]['data'][i]]
    #         constraints += [nodes[0]['time'][i] == nodes[1]['time'][i]]
    #     return Conjunction(constraints)