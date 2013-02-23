RULE_SWITCH=
CHAIN_SWITCH=

case $1 in
add)
	RULE_SWITCH=-A
	CHAIN_SWITCH=-N
;;
del)
	RULE_SWITCH=-D
	CHAIN_SWITCH=-X
;;
*)
	exit 1
esac


iptables -t nat $CHAIN_SWITCH authorized
iptables -t nat $CHAIN_SWITCH not_authorized

#iptables -t nat $RULE_SWITCH PREROUTING -m mac --mac-source 00:16:CB:08:8D:E8 -j authorized
iptables -t nat $RULE_SWITCH PREROUTING -m mac --mac-source 08:00:27:35:F1:04 -j authorized
iptables -t nat $RULE_SWITCH PREROUTING -j not_authorized

iptables -t nat $RULE_SWITCH authorized -j ACCEPT

#iptables -t nat $RULE_SWITCH not_authorized -m state --state NEW,ESTABLISHED,RELATED,INVALID -d "icanhas.cheezburger.com" -j ACCEPT
#iptables -t nat $RULE_SWITCH not_authorized -m state --state NEW,ESTABLISHED,RELATED,INVALID -d "cheezburger.com" -j ACCEPT
#iptables -t nat $RULE_SWITCH not_authorized -m state --state NEW,ESTABLISHED,RELATED,INVALID -d "s.chzbgr.com" -j ACCEPT
#iptables -t nat $RULE_SWITCH not_authorized -m state --state NEW,ESTABLISHED,RELATED,INVALID -d "www.youtube.com" -j ACCEPT
#iptables -t nat $RULE_SWITCH not_authorized -m state --state NEW,ESTABLISHED,RELATED,INVALID -d "i3.ytimg.com" -j ACCEPT

iptables -t nat $RULE_SWITCH not_authorized -p tcp -m multiport --dport 80 -j DNAT --to-destination 192.168.122.1:8080
