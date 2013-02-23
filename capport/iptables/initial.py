STARTUP_TABLES = [
"-t nat -A PREROUTING -j %(NO_AUTH_CHAIN)s",
"-t nat -A %(AUTH_CHAIN)s -j ACCEPT",
"-t nat -A %(NO_AUTH_CHAIN)s -p tcp -m multiport --dport 80 -j DNAT --to-destination %(AP)s",
]
