#!/bin/sh
# set x to 1st argument, y to 2nd argument, and port to 3rd argument
x=$1
y=$2
port=$3

# if x or y is not 0 or 1, then exit
if [ $x -ne 0 ] && [ $x -ne 1 ]; then
    echo "x must be 0 or 1"
    exit 1
fi

if [ $y -ne 0 ] && [ $y -ne 1 ]; then
    echo "y must be 0 or 1"
    exit 1
fi

# if port is a number, then call python with x, y, and port
if [ $port -eq $port 2>/dev/null ]; then
    ./bob.py $y $port & 
    ./alice.py $x $port 
else
    ./bob.py $y &
    ./alice.py $x 
fi

