
import os, datetime, json, queue, functools

def get_current_time() :
    return datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")

def get_datetime_stamp() :
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

def get_one_item_in_queue(q, max_num_items = 10):
    item = None
    try:
        item = q.get_nowait()
    except queue.Empty as e:
        pass
    return item

def put_one_item_to_queue(q, item):
    try :
        q.put_nowait(item)
    except queue.Full as e:
        pass

def get_all_items_in_queue(q, max_num_items = 10):
    items = []
    for i in range(0, max_num_items):
        try:
            items.append(q.get_nowait())
        except queue.Empty as e:
            break
    return items

def put_items_to_queue(q, items):
    for item in items :
        try:
            q.put_nowait(item)
        except queue.Full as e:
            break

def print_problem(pro) :
    print("Problem:")
    print(pro.info())
    print("Variables:")
    for var, domain in pro.vars.items() :
        print("%s -> %s" %(var, domain.info()))
    print("Constraints:")
    for con in pro.cons :
        print("%s : %s" %(con.info(), con.vars))

def view_logs(log_dir, style = "agentbase") :
    # style in one of "timeline", "agentbase"
    logs = {}
    ids = []
    if not os.path.isdir(log_dir) :
        print("cannot find %s." % log_dir)
    else :
        for file in os.listdir(log_dir) :
            name, ext = os.path.splitext(file)
            if ext == ".log" :
                ids.append(name.split("_")[-1])
                with open(os.path.join(log_dir, file), 'r') as f :
                    logs[ids[-1]] = f.readlines()
    if style == "agentbase" :
        for id in sorted(ids) :
            for line in logs[id] :
                print("[agent_%s] %s" % (id, line.strip()))
    elif style == "timeline" :
        sorted_logs = []
        for id in sorted(ids) :
            for line in logs[id] :
                timelabel = '/'.join(line.split(' ')[:2])[1:-1]
                sorted_logs.append((timelabel, "[agent_%s] %s" % (id, line.strip())))
        sorted_logs = sorted(sorted_logs, key = lambda x: x[0])
        for item in sorted_logs:
            print(item[1])
    else :
        print("Invalid style: %s." % style)

def dict_get_wrapper(key, d, default_value) :
    return d.get(key, default_value)

def get_var_host(avars) :
    var_mapping = {}
    for i, vars in enumerate(avars) :
        for var in vars :
           var_mapping[var] = i
    return functools.partial(dict_get_wrapper, d = var_mapping, default_value = None)

def check_dict_compatible(d1, d2) : # return True iff d1 and d2 have the same values for the common keys.
    result = True
    for key, value in d2.items() :
        if key in d1 and value != d1[key] :
            result = False
            break
    return result

def check_dict_contained(d1, d2) : # return True if the key-values in d1 are defined in the same way in d2.
    result = True
    for key, value in d1.items() :
        if key not in d2 or value != d2[key] :
            result = False
            break
    return result

def get_dict_hash(d) :
    return hash(frozenset(d.items()))

def get_constraint_graph(pro, avars) :
    var_host = get_var_host(avars = avars)
    graph = [[] for i in range(len(avars))]
    for con in pro.cons :
        for i in range(len(con.vars)) :
            for j in range(i + 1, len(con.vars)) :
                host_i = var_host(con.vars[i])
                host_j = var_host(con.vars[j])
                if host_j not in graph[host_i] :
                    graph[host_i].append(host_j)
                if host_i not in graph[host_j] :
                    graph[host_j].append(host_i)
    return graph

def get_pseudo_tree(graph) :
    # the tree is returned in a format of list, where the i-th entry contains a tuple
    # consisting of the parent, the list of children, the list of pseudo parents,
    # and the list of pseudo children, of node i.
    tree = [(None, [], [], []) for i in range(len(graph))]
    visited = [False for i in range(len(graph))]
    queue = [(None, 0)]
    while len(queue) > 0 :
        parent, node = queue.pop()
        if visited[node] == False :
            if parent is not None :
                tree[node] = (parent, [], [], [])
                if node not in tree[parent][1] :
                    tree[parent][1].append(node)
            for nb in graph[node] :
                if visited[nb] == False :
                    queue.append((node, nb))
                elif nb != parent :
                    if nb not in tree[node][2] :
                        tree[node][2].append(nb)
                    if node not in tree[nb][3] :
                        tree[nb][3].append(node)
            visited[node] = True
    return tree
