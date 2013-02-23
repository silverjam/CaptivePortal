
from capport.iptables.rulemanager import RuleManagerActions, RuleManager, RuleManagerConfig

class TestActions (RuleManagerActions):
    '''
    Handle system manipulation tasks for rule manager, overriden in tests
    '''

    _runIptables_ret = []
    _runIptables_args = []

    def runIptables(self, args):
        self._runIptables_args.append(args)
        return self._runIptables_ret.pop(0)

    _saveIptables_called = []

    def saveIptables(self):
        self._saveIptables_called.append(True)
        return "savedata"

    _restoreIptables_ret = []
    _restoreIptables_args = []

    def restoreIptables(self, inp):
        self._restoreIptables_args.append(inp)
        return self._restoreIptables_ret.pop(0)

def getConfig():

    cfg = RuleManagerConfig()

    cfg.authorizedChain = "yesyesyes"
    cfg.notAuthorizedChain = "nonono"

    return cfg

MAC = "00:16:CB:08:8D:E8"

def eq_(a, b):
    assert a == b, "%r != %r" % (a, b)

def test_unblock():

    cfg = getConfig()

    actions = TestActions()
    rulemgr = RuleManager(actions, cfg)

    actions._runIptables_ret.append(True)
    rulemgr.unblockUser(MAC)

    r = "-t nat -I PREROUTING -m mac --mac-source 00:16:CB:08:8D:E8 -j yesyesyes"
    eq_(actions._runIptables_args.pop(0), r)

def test_setup_and_teardown():

    cfg = getConfig()
    cfg.accessPoint = "bacon:yes"

    actions = TestActions()
    rulemgr = RuleManager(actions, cfg)
    
    actions._runIptables_ret.append(True)
    actions._runIptables_ret.append(True)
    actions._runIptables_ret.append(True)
    actions._runIptables_ret.append(True)
    actions._runIptables_ret.append(True)

    rulemgr.setUp()
    assert actions._saveIptables_called.pop() == True, "Save iptables was not called"

    eq_( "-t nat -N yesyesyes", actions._runIptables_args.pop(0) )
    eq_( "-t nat -N nonono", actions._runIptables_args.pop(0) )

    eq_( "-t nat -A PREROUTING -j nonono", actions._runIptables_args.pop(0) )
    eq_( "-t nat -A yesyesyes -j ACCEPT", actions._runIptables_args.pop(0) )
    eq_( "-t nat -A nonono -p tcp -m multiport --dport 80 -j DNAT --to-destination bacon:yes", actions._runIptables_args.pop(0) )

    actions._restoreIptables_ret.append(True)
    rulemgr.tearDown()

    eq_( "savedata", actions._restoreIptables_args.pop() )
    

# vim: ts=4:sts=4:et:sw=4:ai:
