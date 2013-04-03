import string
import ssl
import nntplib


class Server(object):
    def __init__(self, host, user, passwd, port=None, use_ssl=False):
        self._host = host
        self._user = user
        self._passwd = passwd
        self._use_ssl = use_ssl

        if self._use_ssl:
            self._port = port if port else 563
            self._ssl_context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        else:
            self._port = port if port else 119

        self.connect()


    def connect(self):
        if self._use_ssl:
            self._server = nntplib.NNTP_SSL(
                host=self._host,
                port=self._port,
                user=self._user,
                password=self._passwd,
                ssl_context=self._ssl_context)
        else:
            self._server = nntplib.NNTP(
                host=self._host,
                port=self._port,
                user=self._user,
                password=self._passwd)
        print('Connected to {0}.'.format(self._host))

    def set_group(self, group):
        resp, count, first, last, name = self._server.group(group)
        return first, last, count

    def fetch_articles(self, group, start_index=None, chunk_size=None):
        print('Reading from group {0}...'.format(group))
        count, first, last = self._server.group(group)
        print('Getting a list of nzb files in {0} ({1} articles found)...'.format(group, count))

        max_run_size = max_run_size if max_run_size else 200000
        chunk_size = chunk_size if chunk_size else 20000
        start_index = start_index if start_index else int(first)
        last_index = int(last)

        if start_index < int(first) and not force_start_index:
            start_index = int(first)

        current_index = start_index

        if (last_index - current_index) > max_run_size and not force_start_index:
            current_index = last_index - max_run_size

        if force_start_index:
            last_index = start_index + max_run_size

        while (current_index < last_index):
            if (current_index + chunk_size >= last_index):
                chunk_size = last_index - current_index

            print('Reading records {0}:{1}.'.format(current_index, current_index + chunk_size))

            try:
                resp, items = self._server.over(str(current_index), str(current_index + chunk_size))
            except:
                print('Server failed to respond, reconnecting...')
                self.connect()
                self._server.group(group)
                resp, items = self._server.over((current_index, current_index + chunk_size))

            for artnum, info in items:
                if '.nzb' in info['subject'].lower():
                    print(('found nzb: {0}'.format(artnum), info))

            current_index += chunk_size

    def quit(self):
        self._server.quit()
        print('Disconnected from {0}.'.format(self._host))
