import persistqueue
from persistqueue.exceptions import Empty

site_queue = persistqueue.UniqueQ("queuefile")

"""
Author: Nicholas Wentz
This module uses the persistqueue library to enqueue and dequeue items from a file-based queue. This is used when web 
crawling to allow for closing and resuming where the crawler left off."""


def enqueue(item):
    """
    This function adds an item (a site url) to the persistqueue (file-based queue)
    :param item: item to add to the persistqueue - should be site url
    :return: None
    """
    site_queue.put(item)


def dequeue():
    """
    This function removes the first item from the persistqueue
    :return: persistqueue.get
    """
    try:
        return site_queue.get(block=False)
    except Empty:
        return None
