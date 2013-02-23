#!/bin/bash

cd `dirname $0`

user=`id -un`
host=`hostname`

echo user=$user
echo host=$host

cat <<EOF >/tmp/sudoers_capport
$user $host = (root) NOPASSWD: $PWD/sudo_iptables
$user $host = (root) NOPASSWD: $PWD/sudo_iptables_save
$user $host = (root) NOPASSWD: $PWD/sudo_iptables_restore
EOF

visudo -c -f /tmp/sudoers_capport
if [ $? -eq 0 ]; then
    sudo cp /tmp/sudoers_capport /etc/sudoers.d/capport
else
    echo "Invalid sudoers files"
fi
