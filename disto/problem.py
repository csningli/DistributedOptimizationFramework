
import numpy as np

class Domain(object) :
    def __init__(self, values) :
        self.values = values

class Constraint(object) :
    def __init__(self, vars) :
        self.vars = vars

    def utility(self, x) :
        return 0

class Problem(object) :
    def __init__(self, vars, cons) :
        self.vars = vars
        self.cons = cons

    def info(self) :
        return f"<<Disto.{type(self).__name__} num_vars = {len(self.vars)}; num_cons = {len(self.cons)}>>"

    def split(self, avars) :
        '''
        split the problem into several sub-problems.
        -------------------------
        avars : a list, where the i-th item is the list of variables assigned to the i-th agent
        '''
        mapping = {}
        for i, vars in enumerate(avars) :
            for var in vars :
                mapping[var] = i
        acons = [[] for i in range(len(avars))]
        for con in self.cons :
            for var in con.vars :
                acons[mapping(var)].append(con)
        pros = [type(self)(vars = avars[i], cons = acons[i]) for i in range(len(avars))]
        return pros

class BinaryDiffConstraint(Constraint) :
    def utility(self, x) :
        return int(x[0] != x[1])

class DiffConstraint(Constraint) :
    def utility(self, x) :
        return int(len(set(x)) >= len(x))

class GraphColoringProblem(Problem) :
    def __init__(self, graph, num_colors = 4) :
        self.graph = graph
        self.num_colors = num_colors
        domain = Domain(values = [i for i in range(self.num_colors)])
        n = self.graph.number_of_nodes()
        vars = {"n%d" % i : domain for i in range(n)}
        cons = []
        for edge in self.graph.edges :
            cons.append(BinaryDiffConstraint(vars = [edge[0], edge[1]]))
        super(GraphColoringProblem, self).__init__(vars = vars, cons = cons)

    def info(self) :
        return f"<<Disto.{type(self).__name__} num_nodes = {len(self.graph.nodes)}; num_edges = {len(self.graph.edges)}; num_colors = {self.num_colors}>>"
