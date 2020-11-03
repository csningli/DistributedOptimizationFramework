
import numpy as np

class Domain(object) :
    def __init__(self, values) :
        self.values = values

    def info(self) :
        return f"<<Disto.{type(self).__name__} num_values = {len(self.values)}>>"

    def first_value(self) :
        return None if len(self.values) < 1 else self.values[0]

    def last_value(self) :
        return None if len(self.values) < 1 else self.values[-1]

    def next_value(self, value) :
        next = None
        if value in self.values :
            index = self.values.index(value) + 1
            if index < len(self.values) :
                next = self.values[index]
        return next

def init_assign(vars, order_list = None) :
    order_list = sorted(list(vars.keys())) if order_list is None else order_list
    assign = {}
    for var in order_list :
        assign[var] = vars[var].first_value()
    return assign

def next_assign(assign, vars, order_list = None) :
    order_list = sorted(list(assign.keys())) if order_list is None else order_list
    order_list.reverse()
    next = assign
    for i, var in enumerate(order_list) :
        if assign[var] != vars[var].last_value() :
            assign[var] = vars[var].next_value(assign[var])
            for j in range(i) :
                assign[order_list[j]] = vars[order_list[j]].first_value()
    return assign

def cover_cons(cons, assign) :
    cons = []
    for con in cons :
        covered = True
        for var in con.vars :
            if not next.has_key(var) :
                covered = False
                break
        if covered == True :
            cons.append(con)
    return cons

def total_utility(cons, assign) :
    u = None
    for con in cons :
        v = con.fit(assign)
        u = None if v is None else u + v
    return u

def fix_assign(pro, assign, order_list = None) :
    order_list = sorted(list(pro.vars.keys())) if order_list is None else order_list
    fixed = assign
    cons = cover_cons(pro.cons, assign)
    u = total_utility(cons, fixed)
    while u is None :
        next = next_assign(fixed, pro.vars, order_list)
        if next == fixed :
            break
        else :
            fixed = next
        u = total_utility(cons, fixed)
    return fixed

class Constraint(object) :
    def __init__(self, vars) :
        self.vars = vars

    def info(self) :
        return f"<<Disto.{type(self).__name__} num_vars = {len(self.vars)}>>"

    def utility(self, x) :
        return 0

class Problem(object) :
    def __init__(self, vars, cons) :
        '''
        vars : dict of var - domain pairs;
        cons : list of constraints.
        '''
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
                acons[mapping[var]].append(con)
        pros = [Problem(vars = {var : self.vars[var] for var in avars[i]}, cons = acons[i]) for i in range(len(avars))]
        return pros

class BinaryDiffConstraint(Constraint) :
    def utility(self, x) :
        return 0 if x[0] != x[1] else None

class DiffConstraint(Constraint) :
    def utility(self, x) :
        return 0 if len(set(x)) >= len(x) else None

class GraphColoringProblem(Problem) :
    def __init__(self, graph, num_colors = 4) :
        self.graph = graph
        self.num_colors = num_colors
        domain = Domain(values = [i for i in range(self.num_colors)])
        n = self.graph.number_of_nodes()
        vars = {"%d" % i : domain for i in range(n)}
        cons = []
        for edge in self.graph.edges :
            cons.append(BinaryDiffConstraint(vars = [edge[0], edge[1]]))
        super(GraphColoringProblem, self).__init__(vars = vars, cons = cons)

    def info(self) :
        return f"<<Disto.{type(self).__name__} num_nodes = {len(self.graph.nodes)}; num_edges = {len(self.graph.edges)}; num_colors = {self.num_colors}>>"
