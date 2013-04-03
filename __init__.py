#!/usr/bin/env python3
import multiprocessing
import os
import signal
import time
import pprint

from server import Server
from config import *


def article_worker(host, user, passwd, port, use_ssl, group, start_index,
                   chunk_size, results, lock, min_index):
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    s = Server(host, user, passwd, port, use_ssl)
    s.set_group(group)

    while start_index.value > min_index:
        # increment start_index here so no two processes end up pulling the same data
        with lock:
            if start_index.value < min_index:
                continue

            upper_limit = start_index.value
            lower_limit = start_index.value - chunk_size

            start_index.value = (start_index.value - chunk_size + 1)
            if lower_limit < min_index:
                lower_limit = min_index

        results.append(s.fetch_articles(group, lower_limit, upper_limit))

    # close the connection here so we can process another group
    s.quit()


def main():
    main_server_instance = Server(HOST, user=USER, passwd=PASSWD, port=PORT, use_ssl=USE_SSL)
    manager = multiprocessing.Manager()
    lock = multiprocessing.Lock()

    for group in GROUPS:
        workers = []
        # get group info here.
        first, last, count = main_server_instance.set_group(group)

        start_index = multiprocessing.Value('i', last)
        results = manager.list()
        args = (HOST, USER, PASSWD, PORT, USE_SSL, group, start_index,
                CHUNK_SIZE, results, lock, first)

        for i in range(1, MAX_CONNECTIONS):
            p = multiprocessing.Process(target=article_worker, args=args)
            p.start()
            workers.append(p)

        try:
            for worker in workers:
                worker.join()
        except KeyboardInterrupt:
            for worker in workers:
                worker.terminate()
                worker.join()

        for worker in workers:
            worker.terminate()
            worker.join()

        print(first, start_index.value, last)


if __name__ == "__main__":
    main()
