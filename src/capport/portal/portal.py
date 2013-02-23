import os
import sys
from datetime import datetime
from optparse import OptionParser
from ConfigParser import RawConfigParser

from twisted.application import internet
from twisted.internet import reactor
from twisted.python import log
from twisted.web import server, static, proxy
from twisted.web.util import redirectTo

SERVER_PORT = 8080

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_PAGE = os.path.join(THIS_DIR, 'page.html')

CHZBURGER_HOSTS = [
    'icanhas.cheezburger.com',
    'cheezburger.com',
    's.chzbgr.com',
    'www.youtube.com',
    'i3.ytimg.com',
    ]

class PortalResource(static.File):

    def __init__(self):
        static.File.__init__(self, ROOT_PAGE)

    def getChild(self, path, request):

        if path == "agreement.html":
            return static.File(os.path.join(THIS_DIR, "agreement.html"))

        for proxyhost in CHZBURGER_HOSTS:
            if path.startswith(proxyhost):
                log.msg(path)
                return proxy.ReverseProxyResource(proxyhost, 80, '/')

        return self


def main():

    log.startLogging(sys.stdout)
    site = server.Site(PortalResource())
    service = internet.TCPServer(SERVER_PORT, site)
    service.startService()
    reactor.run()

if __name__ == '__main__':
    main()


# vim: ts=4:sts=4:et:sw=4:ai:
