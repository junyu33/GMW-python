#!/bin/sh
# 0 for alice, 1 for bob 
person=$1
bit=$2
ip=$3
port=$4

# if x or y is not between 0 to 32, then exit
if [ $bit -le -1 ] && [ $bit -ge 32 ]; then
    echo "bit must be 0 to 255"
    exit 1
fi

# if port is a number, then call python with x, y, and port
if [ $port -eq $port 2>/dev/null ]; then
    if [ $person -eq 1 ]; then
        ./bob.py $bit $ip $port
    else
        ./alice.py $bit $ip $port 
    fi
elif [ $ip -eq $ip 2>/dev/null ]; then
    if [ $person -eq 1 ]; then
        ./bob.py $bit $ip 
    else
        ./alice.py $bit $ip 
    fi
else
    if [ $person -eq 1 ]; then
        ./bob.py $bit
    else
        ./alice.py $bit 
    fi
fi

