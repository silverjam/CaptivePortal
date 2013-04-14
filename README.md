# Captive Portal Tech Challenge

## Video and introduction

I made a short demo of the *captive portal*, it can be seen here:

 - [WiFast Tech Challenge](http://bit.ly/UUxbVq)

...blame linux for the cell phone video (for not having a decent screen
recording package).

The following package uses pip and virtualenv.  So a functional deployment
requires creatinga virtualenv:

    cd <project/root>
    virtualenv venv
    . ./venv/bin/activate

Then installing the required software:

    pip -r requirement.txt

One script needs to be run to set up sudo (*please examine this script before
running it, it could brick your sudoers files*):

    ./scripts/setup_sudoers.sh 

Next, the captive portal server can be launched as follows:

    ./runserver

The tests can be run as follows:

    ./tests/runtests.sh

Please note, the following files attempt to describe the network setup (which
is required to reproduce the demo video):

    brctl.txt
    ifconfig.txt
    iptables.txt
    ./scripts/bridgenic.sh

The core of the implementation is basically the RuleManager class:

  - **RuleManager.unblockUser**: adds a new iptables rule to allow the user through

  - **RuleManager.setUp**: saves the current state of iptables, so the portal
    rules can be cleared on exit

  - **RuleManager.tearDown**: uses the saved rules to restore iptables to its
    previous state-- this function has a "race condition" of sorts, if someone
    else alters the tables while the captive portal is running, the changes could
    be lost.

## Iptables rules

**Q:** What where the iptables rules you used and why?

**A:** The rules used employed 2 chains to acheive an "OR list" of allowed
IPs-- IPs allowed to access the network required new rules to be inserted at
the head of the list of rules so skip the package to the "allowed" chain.

## Example

    iptables -t nat -N authorized
    iptables -t nat -N not_authorized

    iptables -t nat -A PREROUTING \
        -m mac --mac-source 00:16:CB:08:8D:E8 -j authorized
    iptables -t nat -A PREROUTING \
        -m mac --mac-source 08:00:27:35:F1:04 -j authorized
    iptables -t nat -A PREROUTING -j not_authorized

    iptables -t nat -A authorized -j ACCEPT

    iptables -t nat -A not_authorized -p tcp \
        -m multiport --dport 80 -j DNAT --to-destination 192.168.122.1:8080

## Network setup

The test environment had the following setup:

  - wlan0 - host WAN adapter, iptables rules were setup to NAT through this device

  - virbr1 - virtual bridge

  - virbr1-nic - virtual NIC for the VM to bridge with and connect to the NAT

## NAT and PREROUTING

The built-in PREROUTING chain of the NAT table is required to alter packets
that are traveling through the NAT-- as was the case with this network setup.
One thing I'm unsure of is whether it would've been easier to use the *filter*
table to modify traffic on the local device.

For locally generated traffic, which doesn't need to go through the NAT, none
of the above rules apply-- it's possible I could have generated similar rules
and just allowed/denied the MAC address of my local card.

However, I think the current scenario is more realistic.

# General architecture of the full system

I went ahead and implemented part 2, because it seemed relatively simple.  The
solution uses Twisted-- serves up a landing page using a reverse proxy (this
could also be done with iptables), and when the users browser does a POST to a
particular URL, the MAC address of the client is added to an allowed list.

Additional details follow:

## The server and the router are the same box

Since the server and the router are the same box, and everybody exists on the
same network segment, we can detect the MAC addresses of the incoming packets.
The server blocks these MAC addresses until the user has "authenticated" in some
way.

## Authenticated MAC addresses

Authenticated MAC address have a rule add to skip them past the rules that
force all packets to go to the portal.  These stay in memory until the portal
server is restarted.

## Security concerns

Sudo was used to invoke iptables, but future implementations should probably
take more care to seperate out the part of the sever (into a privsep / isolated
scenario) that interacts with root.
