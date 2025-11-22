from channel import *

import sys

class Connector:  # Used to represent the connection relationships between system components.
    # Create an empty list to store the connection information between channels and nodes.
    def __init__(self):
        self.channels = []

    # Method for adding channel-node connection relationships
    # Parameters: channel is the channel type name, *nodes is a list of node names
    def connect(self, channel, *nodes):
        self.channels += [(channel, nodes)]
        return self

    def isRefinementOf(self, abstraction, bound):
        assert isinstance(abstraction, Connector)
        nodes = {}

        solver = Solver()

        # generate variables for the refinement
        for chan in self.channels:
            for nd in chan[1]:
                if nd not in nodes:
                    nodes[nd] = {
                        'time': [Real(nd + '_t_' + str(i)) for i in range(bound)],
                        'data': [Int(nd + '_d_' + str(i)) for i in range(bound)]
                        }

                    solver.add(nodes[nd]['time'][0] >= 0)
                    for i in range(bound - 1):
                        solver.add(nodes[nd]['time'][i] < nodes[nd]['time'][i + 1])

                    for i in range(bound):
                        solver.add(Or(nodes[nd]['data'][i] < 10, nodes[nd]['data'][i] > 20))

            # generate constraint for channels
            channelDecl = eval('Channel.' + chan[0])
            paramnodes = list(map(lambda name: nodes[name], chan[1]))
            solver.add(channelDecl(paramnodes, bound))

        # deal with the abstraction
        foralls = []
        absGlobalConstr = None  # Abstract global constraints(conjunction of channel constraints)
        absTimeConstr = None  # Abstract time constraints(conjunction of node time increment constraints)

        for chan in abstraction.channels:
            for nd in chan[1]:
                if nd not in nodes:
                    nodes[nd] = {
                        'time': [Const(nd + '_t_' + str(i), RealSort()) for i in range(bound)],
                        'data': [Const(nd + '_d_' + str(i), IntSort()) for i in range(bound)]
                        }

                    foralls += nodes[nd]['time']
                    foralls += nodes[nd]['data']

                    currTimeConstr = (nodes[nd]['time'][0] >= 0)
                    for i in range(bound - 1):
                        currTimeConstr = And(currTimeConstr, nodes[nd]['time'][i] < nodes[nd]['time'][i + 1])

                    currDataConstr = True
                    for i in range(bound):
                        currDataConstr = And(currDataConstr, Or(nodes[nd]['data'][i] < 10, nodes[nd]['data'][i] > 20))

                    currNodeConstr = And(currTimeConstr, currDataConstr)

                    # Merge into the total abstract time constraints (conjunction of multiple nodes' time constraints)
                    if absTimeConstr is None:
                        absTimeConstr = currNodeConstr
                    else:
                        absTimeConstr = And(absTimeConstr, currNodeConstr)

            # generate constraint for channels
            channelDecl = eval('Channel.' + chan[0])
            paramnodes = list(map(lambda name: nodes[name], chan[1]))

            constr = channelDecl(paramnodes, bound)
            if absGlobalConstr is None:
                absGlobalConstr = constr
            else:
                absGlobalConstr = And(constr, absGlobalConstr)

        if absTimeConstr is not None:
            absGlobalConstr = Or(Not(absTimeConstr), Not(absGlobalConstr))
        else:
            absGlobalConstr = Not(absGlobalConstr)

        # deal with the constraints of abstraction
        if foralls != []:
            solver.add(ForAll(foralls, absGlobalConstr))
        else:
            solver.add(absGlobalConstr)
        # TODO: time constraints of the nodes in forall should be put into absGlobalConstr
        # @liyi test if the todo techniques work
        result = solver.check()

        # DEBUG USE
        if 'counterexample' in sys.argv and str(result) == 'sat':
            print(solver.model())

        # For debugging: if command line arguments include 'smt2', print constraints in SMT-LIB 2 format
        if 'smt2' in sys.argv:
            print(solver.to_smt2())

        # Return based on solving result:
        if str(result) == 'sat':
            return False, solver.model(), solver.to_smt2()
        else:
            return True, None, solver.to_smt2()
        pass
