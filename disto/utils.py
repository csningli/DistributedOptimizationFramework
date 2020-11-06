
import os, datetime, json, queue

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
