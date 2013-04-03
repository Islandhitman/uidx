import string
import ssl
import nntplib
import os


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

    def fetch_articles(self, group, lower_limit=None, upper_limit=None):
        print('Reading from group {0}...'.format(group))
        self._server.group(group)

        print('Reading records {0}:{1}.'.format(lower_limit, upper_limit))

        try:
            resp, items = self._server.over((str(lower_limit), str(upper_limit)))
        except:
            print('Server failed to respond, reconnecting...')
            self.connect()
            self._server.group(group)
            resp, items = self._server.over((str(lower_limit), str(upper_limit)))

        for artnum, info in items:
            if '.nzb' in info['subject'].lower():
                print(('found nzb: {0}'.format(artnum), info))

    def quit(self):
        self._server.quit()
        print('Disconnected from {0}.'.format(self._host))
