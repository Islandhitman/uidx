#!/usr/bin/env python3
import multiprocessing
import os
import signal
import time
import Queue

from uidx.server import Server


HOST = 'news.example.com'
USER = 'example_user'
PASSWD = 'example_password'
PORT = 563
USE_SSL = True
DAYS = 300
CHUNK_SIZE = 20000
MAX_CONNECTIONS = 30
GROUPS = ['alt.binaries.test']


def worker(host, user, passwd, port, use_ssl, group, start_index, chunk_size, results):
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    s = Server(host, user, passwd, port, use_ssl)
    s.set_group(group)

    while not article_queue.empty():
        try:
            # increment start_index here so no two processes end up pulling the same data
            start_index.value = (start_index + chunk_size + 1)
            results.append(s.fetch_articles(group, (start_index - chunk_size - 1), chunk_size))
        except Queue.Empty:
            pass

    # close the connection here so we can process another group
    s.quit()


def main():
    main_server_instance = Server(HOST, USER, PASSWD, PORT, USE_SSL)
    manager = multiprocessing.Manager()

    for group in GROUPS:
        workers = []
        # get group info here.
        first, last, count = main_server_instance.set_group(group, DAYS)

        start_index = multiprocessing.Value('i', first)
        last_index = last
        results = manager.list()
        args = (HOST, USER, PASSWD, PORT, USE_SSL, group, start_index,
                chunk_size, results)

        for i in range(1, MAX_CONNECTIONS):
            p = multiprocessing.Process(target=worker, args=args)
            p.start()
            workers.append(p)

            try:
                for worker in workers:
                    worker.join()
            except KeyboardInterrupt:
                for worker in workers:
                    worker.terminate()
                    worker.join()

        while not result_queue.empty():
            # DB storage will eventually occur here.
            print result_queue.get(block=False)


if __name__ == "__main__":
    main()
