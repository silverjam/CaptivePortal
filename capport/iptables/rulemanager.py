# -*- python -*-

import subprocess

from twisted.python import log
from twisted.python.procutils import which

from . import initial

class RuleManagerActions (object):
    '''
    Handle system manipulation tasks for rule manager, overriden in tests
    '''

    def runIptables(self, args):
        iptables = which("sudo_iptables")[0]
        cmd = [ "sh", "-c", "sudo " + iptables + " " + args ]
        return subprocess.call(cmd)

    def saveIptables(self):
        cmd = [ "sh", "-c", "sudo " + which("sudo_iptables_save")[0] ]
        return subprocess.check_output(cmd)

    def restoreIptables(self, inp):
        cmd = [ "sh", "-c", "sudo " + which("sudo_iptables_restore")[0] ]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        #print inp
        p.communicate(inp)
        return p.returncode == 0


class RuleManagerConfig (object):
    '''
    Basic configuration settings for the rule manager
    '''

    authorizedChain = 'authorized'
    notAuthorizedChain = 'not_authorized'

    ruleTemplate = "-t nat %(SWITCH)s %(CHAIN)s -m mac --mac-source %(MAC)s -j %(TARGET)s"
    chainTemplate = "-t nat %(SWITCH)s %(NAME)s"

    addRuleSwitch = "-I"
    removeRuleSwitch = "-D"

    addChainSwitch = "-N"
    removeChainSwitch = "-X"

    accessPoint = "192.168.122.1:8080"


class RuleManager (object):
    '''
    This class manages iptables rules for allowing users out of the
    portal
    '''

    def __init__(self, ruleActions = None, config = None):

        if ruleActions != None:
            self._actions = ruleActions
        else:
            self._actions = RuleManagerActions()

        if config != None:
            self._config = config
        else:
            self._config = RuleManagerConfig()

        self._saveData = ''

    def _buildRule(self, mac, chain, blocked, adding):

        if adding:
            switch = self._config.addRuleSwitch
        else:
            switch = self._config.removeRuleSwitch

        if blocked:
            target = self._config.notAuthorizedChain
        else:
            target = self._config.authorizedChain

        params = {
            'SWITCH' : switch,
            'MAC' : mac,
            'TARGET' : target,
            'CHAIN' : chain,
            }

        return self._config.ruleTemplate % params
    
    def _buildChain(self, name, adding):
 
        if adding:
            switch = self._config.addChainSwitch
        else:
            switch = self._config.removeChainSwitch

        params = {
            'SWITCH' : switch,
            'NAME' : name
        }
       
        return self._config.chainTemplate % params

    def _buildUnblock(self, mac):
        return self._buildRule(mac, 'PREROUTING', False, True)

    def setUp(self):
        self._saveData = self._actions.saveIptables() 
        self.setupChains()
        cfg = { 'NO_AUTH_CHAIN' : self._config.notAuthorizedChain,
                'AUTH_CHAIN'    : self._config.authorizedChain,
                'AP'            : self._config.accessPoint }
        for rule in initial.STARTUP_TABLES:
            self._actions.runIptables(rule % cfg)

    def tearDown(self):
        self._actions.restoreIptables(self._saveData) 

    def unblockUser(self, mac):
        rule = self._buildUnblock(mac)
        if not self._actions.runIptables(rule):
            log.msg("Adding rule failed: %s" % (rule,))

    def setupChains(self):
        chains = [ self._config.authorizedChain,
                   self._config.notAuthorizedChain ]
        for name in chains:
            chain = self._buildChain(name, True)
            if not self._actions.runIptables(chain):
                log.msg("Adding chain failed: %s" % (chain,))


# vim: ts=4:sts=4:et:sw=4:ai:
