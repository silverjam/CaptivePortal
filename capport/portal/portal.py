# -*- python -*-

import os
import re
import sys
import cgi
import subprocess

from twisted.application import internet
from twisted.internet import reactor
from twisted.python import log
from twisted.web import server, static, proxy, resource
from twisted.web.util import redirectTo

from capport.iptables.rulemanager import RuleManager


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

GOOG_HOSTS = [
    'google.com',
    'www.google.com',
    'ssl.gstatic.com',
]

WIKI_HOSTS = [
    'en.wikipedia.org',
    'bits.wikimedia.org',
    'upload.wikimedia.org',
    'donate.wikimedia.org',
    'meta.wikimedia.org',
    'creativecommons.org',
    'wikimediafoundation.org',
    'www.wikimediafoundation.org',
]

BROWSE_HOSTS = WIKI_HOSTS

class FormPage(resource.Resource):

    def __init__(self, rulemgr):
        self._rulemgr = rulemgr

    def render_GET(self, request):
        return '<html><body><p>Nothing here, use POST instead of GET.</p></body></html>'

    def render_POST(self, request):

        cmd = ["arp", "-n", request.getClientIP()]
        print cmd

        pid = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        arp_output = pid.communicate()[0]
        
        if arp_output:
            mac = re.search(r"(([a-f\d]{1,2}\:){5}[a-f\d]{1,2})", arp_output).groups()[0]
            log.msg("User accepted the agreement: ", mac)

            self._rulemgr.unblockUser(mac)

        return '<html><body>Thanks!</body></html>'


class PortalResource(static.File):

    def __init__(self, rulemgr):
        static.File.__init__(self, ROOT_PAGE)
        self._rulemgr = rulemgr

    def getChild(self, path, request):

        if path == "agreement.html":
            return static.File(os.path.join(THIS_DIR, "agreement.html"))

        if path == "iaccepttheboringagreement":
            return FormPage(self._rulemgr)

        for proxyhost in BROWSE_HOSTS:
            if path.startswith(proxyhost):
                log.msg(path)
                return proxy.ReverseProxyResource(proxyhost, 80, '/')
            reqHost = request.getRequestHostname()
            if reqHost.startswith(proxyhost):
                log.msg(reqHost)
                return proxy.ReverseProxyResource(reqHost, 80, '/' + path)

        return self


def main():

    log.startLogging(sys.stdout)
    rulemgr = RuleManager()
    site = server.Site(PortalResource(rulemgr))
    service = internet.TCPServer(SERVER_PORT, site)
    service.startService()

    try:
        rulemgr.setUp()
        reactor.run()

    finally:
        rulemgr.tearDown()

if __name__ == '__main__':
    main()


# vim: ts=4:sts=4:et:sw=4:ai:
