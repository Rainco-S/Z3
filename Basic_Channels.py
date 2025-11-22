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
            if i != 0:
                constraints += [nodes[0]['time'][i] > nodes[1]['time'][i-1]]
        return Conjunction(constraints)
    
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
    def LossySync(nodes, bound, idx = 0, num = 0):
        assert len(nodes) == 2
        if num == bound: # nodes[1] is full
            return True
        if idx == bound: # nodes[0] is full
            return True
        constraints_0, constraints_1 = [], []

        constraints_0 += [nodes[0]['time'][idx] != nodes[1]['time'][num]] # drop

        constraints_1 += [nodes[0]['data'][idx] == nodes[1]['data'][num]] # transmit
        constraints_1 += [nodes[0]['time'][idx] == nodes[1]['time'][num]]
        
        return Or(
            And(Conjunction(constraints_0), Channel.LossySync(nodes, bound, idx + 1, num)),
            And(Conjunction(constraints_1), Channel.LossySync(nodes, bound, idx + 1, num + 1))
        )
    
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
    def Producerp(p): # DIY
        # p also a list here
        def ProducerpInstance(nodes, bound):
            assert len(nodes) == 2
            constraints = []
            for i in range(bound):
                constraints += [Disjunction([nodes[1]['data'][i] == v for v in p])]
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
            if a[i] < b[j]:
                return And(a[i] != b[j], Asyn(a, b, i + 1, j))
            else:
                return And(a[i] != b[j], Asyn(a, b, i, j + 1))
        
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
            if a[i] < b[j]:
                return And(a[i] != b[j], Asyn(a, b, i + 1, j))
            else:
                return And(a[i] != b[j], Asyn(a, b, i, j + 1))

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
    def Replicator(nodes, bound): # DIY 0 --> 1, 2
        assert len(nodes) == 3
        constraints = []
        for i in range(bound):
            constraints += [nodes[0]['data'][i] == nodes[1]['data'][i]]
            constraints += [nodes[0]['time'][i] == nodes[1]['time'][i]]
            constraints += [nodes[0]['data'][i] == nodes[2]['data'][i]]
            constraints += [nodes[0]['time'][i] == nodes[2]['time'][i]]
        return Conjunction(constraints)
    
    @staticmethod
    def FlowThrough(nodes, bound): # DIY 0 --> _ --> 2
        assert len(nodes) == 2
        constraints = []
        for i in range(bound):
            constraints += [nodes[0]['data'][i] == nodes[1]['data'][i]]
            constraints += [nodes[0]['time'][i] == nodes[1]['time'][i]]
        return Conjunction(constraints)
        