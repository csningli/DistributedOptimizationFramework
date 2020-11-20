
import numpy, copy

from disto.utils import *

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
    next = copy.deepcopy(assign)
    for i in range(len(order_list) - 1, -1, -1) :
        var = order_list[i]
        if next[var] != vars[var].last_value() :
            next[var] = vars[var].next_value(next[var])
            for j in range(i + 1, len(order_list)) :
                next[order_list[j]] = vars[order_list[j]].first_value()
            break
    return next

def cover_cons(cons, assign) :
    cover = []
    for con in cons :
        for var in con.vars :
            if var in assign :
                cover.append(con)
                break
    return cover

def fit_assign_to_con(assign, con) :
    x = []
    for var in con.vars :
        if var in assign :
            x.append(assign[var])
        else :
            x = None
            break
    return x

def calc_cost(con, assign) :
    cost = 0
    x = fit_assign_to_con(assign, con)
    if x is not None :
        cost = con.cost(x)
    return cost

def total_cost(cons, assign) :
    cost = 0
    violated = []
    for con in cons :
        c = calc_cost(con, assign)
        if c is None :
            cost = None
            violated.append(con)
            break
        else :
            cost += c
    if cost is not None :
        violated = []
    return cost, violated

def fix_assign(pro, assign, order_list = None) :
    order_list = sorted(list(pro.vars.keys())) if order_list is None else order_list
    fixed = copy.deepcopy(assign)
    cons = cover_cons(pro.cons, assign)
    violated = []
    cost, v = total_cost(cons, fixed)
    while cost is None :
        violated += [con for con in v if con not in violated]
        next = next_assign(fixed, pro.vars, order_list)
        if next == fixed :
            break
        else :
            fixed = next
            cost, v = total_cost(cons, fixed)
    return fixed, cost, violated

class Constraint(object) :
    def __init__(self, vars) :
        self.vars = vars

    def info(self) :
        return f"<<Disto.{type(self).__name__} num_vars = {len(self.vars)}>>"

    def valid(self, x) :
        v = True
        for var in self.vars :
            if var not in x :
                v = False
        return v

    def cost(self, x) :
        return 0

class BinaryDiffConstraint(Constraint) :
    def cost(self, x) :
        return 0 if x[0] != x[1] else None

class DiffConstraint(Constraint) :
    def cost(self, x) :
        return 0 if len(set(x)) >= len(x) else None

class ForbiddenConstraint(Constraint) :
    def __init__(self, vars, values) :
        super(ForbiddenConstraint, self).__init__(vars = vars)
        self.values = values

    def cost(self, x) :
        return 0 if x not in self.values else None

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

    def split(self, avars, con_host = None) :
        '''
        split the problem into several sub-problems.
        -------------------------
        avars : a list, where the i-th item is the list of variables assigned to the i-th agent
        con_host : a function return variables whose host agents will know the given constraint
        '''
        var_host = get_var_host(avars = avars)
        acons = [[] for i in range(len(avars))]
        for con in self.cons :
            ids = set([var_host(var) for var in con.vars]) if con_host is None else con_host(con)
            for id in ids :
                acons[id].append(con)
        pros = [Problem(vars = {var : self.vars[var] for var in avars[i]}, cons = acons[i]) for i in range(len(avars))]
        return pros

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
