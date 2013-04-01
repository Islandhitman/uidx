import string
import datetime
import time
import ssl
import nntplib


class Server(object):
    def __init__(self, host, user, password, use_ssl=False, port=None):
        self._host = host
        self._user = user
        self._pass = password
        self._use_ssl = use_ssl

        if self._use_ssl:
            self._port = port if port else 563
        else:
            self._port = port if port else 119

    def _connect(self):
        if self._use_ssl:
            self._server = nntplib.NNTP_SSL(host=self._host, port=self._port,
                                            user=self._user, password=self._password, ssl)
        else:
            self._server = nntplib.NNTP(host=self._host, port=self._port,
                                        user=self._user, password=self._password)
