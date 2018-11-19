import persistqueue
from persistqueue.exceptions import Empty

site_queue = persistqueue.UniqueQ("queuefile")


def enqueue(item):
    site_queue.put(item)


def dequeue():
    try:
        return site_queue.get(block=False)
    except Empty:
        return None
