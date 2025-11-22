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

    '''
    1.The code first defines Z3 variables for each node in the concrete model, representing their data and time within 
    a given number of steps. Then, it adds constraints to the Z3 solver that define the concrete model's behavior, 
    with these constraints originating from the channels and nodes connected within the specific Connector object.
    2.Next, the code defines variables for the abstract model. If any nodes in the abstract model don't exist in the 
    concrete model, they are treated as universally quantified variables using the ForAll keyword. This means Z3 must 
    check if the abstract constraints hold true for any possible value of these abstract variables, not just a specific one.
    3.The core of the refinement check is based on a logical implication: "If the concrete model's behavior is possible, 
    then the abstract model's constraints must also be satisfied."
    4.Z3 checks this using a method called Satisfiability Modulo Theories (SMT). It negates the refinement condition and 
    asks Z3 to find a solution (a "satisfiable" result). The negated condition is: "The concrete model's constraints are 
    satisfied, AND the abstract model's constraints are NOT satisfied."
    -If Z3 finds a solution to this negated condition, it means a counterexample exists—the concrete model's behavior is 
    valid, but it violates the abstract model's rules. In this case, the concrete model is not a refinement.
    -If Z3 proves this negated condition is unsatisfiable (unsat), it means no such counterexample exists. The implication 
    holds, and the concrete model is a refinement of the abstract model.
    Because Z3 can only handle "satisfiability" problems, it looks for a counterexample to what we want to prove. If it 
    finds that "a concrete model behavior exists that violates the abstract model's constraints," it proves that the model 
    is not a refinement.
    '''
    # Check if the current Connector is a "refinement" of another abstract Connector
    # Refinement means the current instance's behavior fully satisfies the abstract constraints
    # Parameters: abstraction is the abstract Connector instance, bound is the step boundary for checking
    def isRefinementOf(self, abstraction, bound):
        assert isinstance(abstraction, Connector)
        nodes = {}

        solver = Solver()

        # step 1. generate variables for the refinement
        for chan in self.channels:
            # generate constraint for variables (if not existing)
            for nd in chan[1]:
                if nd not in nodes:
                    nodes[nd] = {
                        # Time variables are Real type, named as: nodeName_t_stepNumber
                        # Data variables are Int type, named as: nodeName_d_stepNumber
                        'time': [Real(nd + '_t_' + str(i)) for i in range(bound)],
                        'data': [Int(nd + '_d_' + str(i)) for i in range(bound)]
                        }

                    # generate time constraints: Initial time (step 0) >= 0
                    solver.add(nodes[nd]['time'][0] >= 0)
                    # Time of each step is strictly less than the next step (time is strictly increasing)
                    for i in range(bound - 1):
                        solver.add(nodes[nd]['time'][i] < nodes[nd]['time'][i + 1])

                    for i in range(bound):
                        solver.add(Or(nodes[nd]['data'][i] < 10, nodes[nd]['data'][i] > 20))

            # generate constraint for channels
            channelDecl = eval('Channel.' + chan[0])
            paramnodes = list(map(lambda name: nodes[name], chan[1]))
            # Call the channel constraint function to generate constraints for this channel within bound steps
            # and add to the solver
            solver.add(channelDecl(paramnodes, bound))

        # step 2. deal with the abstraction
        # create constants if needed
        foralls = []
        absGlobalConstr = None  # Abstract global constraints(conjunction of channel constraints)
        absTimeConstr = None  # Abstract time constraints(conjunction of node time increment constraints)

        for chan in abstraction.channels:
            for nd in chan[1]:
                if nd not in nodes:
                    # If node is not in nodes (i.e., it's unique to the abstraction and not in the concrete instance)
                    # Create constant variables for abstract nodes (need universal quantification)
                    # Time variables are of RealSort(), data variables are of IntSort()
                    nodes[nd] = {
                        'time': [Const(nd + '_t_' + str(i), RealSort()) for i in range(bound)],
                        'data': [Const(nd + '_d_' + str(i), IntSort()) for i in range(bound)]
                        }

                    # Add abstract node's time and data variables to the universal quantification list
                    foralls += nodes[nd]['time']
                    foralls += nodes[nd]['data']

                    # Generate time constraints for this abstract node: initial time >= 0 and time is strictly increasing
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

        '''
        Construct the negated form of abstract constraints (for refinement checking)
        Logic: If abstract time constraints are satisfied, then abstract channel constraints must be satisfied;
        otherwise the current instance does not violate the abstraction
        After negation: Abstract time constraints are satisfied AND abstract channel constraints are not
        (in this case, the current instance is not a refinement)
        '''
        if absTimeConstr is not None:
            absGlobalConstr = Or(Not(absTimeConstr), Not(absGlobalConstr))
        else:
            absGlobalConstr = Not(absGlobalConstr)

        # deal with the constraints of abstraction
        if foralls != []:
            # Universally quantify over abstract node variables: for all possible values of abstract nodes,
            # the abstract constraints must hold
            solver.add(ForAll(foralls, absGlobalConstr))
        else:
            solver.add(absGlobalConstr)
        # TODO: time constraints of the nodes in forall should be put into absGlobalConstr
        # @liyi test if the todo techniques work
        result = solver.check()

        # DEBUG USE
        # For debugging: if command line arguments include 'counterexample' and constraints are satisfiable
        # (counterexample exists), print the model
        if 'counterexample' in sys.argv and str(result) == 'sat':
            print(solver.model())

        # For debugging: if command line arguments include 'smt2', print constraints in SMT-LIB 2 format
        if 'smt2' in sys.argv:
            print(solver.to_smt2())

        # Return based on solving result:
        # If constraints are satisfiable (sat), a counterexample exists - current instance is not a refinement
        # Otherwise (unsat), current instance is a refinement
        if str(result) == 'sat':
            return False, solver.model(), solver.to_smt2()
        else:
            return True, None, solver.to_smt2()
        pass

