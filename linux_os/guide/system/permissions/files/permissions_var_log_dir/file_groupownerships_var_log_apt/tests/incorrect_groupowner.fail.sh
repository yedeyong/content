#!/bin/bash
# platform = Ubuntu 24.04

getent group "adm" &>/dev/null || groupadd adm
mkdir -p /var/log/apt
touch /var/log/apt/testfile
chgrp nogroup /var/log/apt/testfile
