
import os, datetime, queue

def get_current_time() :
    return datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")

def get_datetime_stamp() :
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

def get_all_items_in_queue(q, max_num_items = 10):
    items = []
    for i in range(0, max_num_items):
        try:
            items.append(q.get_nowait())
        except Empty, e:
            break
    return items
