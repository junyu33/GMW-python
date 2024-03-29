# simple GMW protocol python implementation

This is a simple implementation of the GMW protocol in python. The GMW protocol is a secure multi-party computation protocol that allows multiple parties to compute a function on their inputs without revealing their inputs to each other. 

## requirements

- python3.8+

## Usage

modify your gates in the `gates.py` file, and then run `start.sh`. The result will be printed to the console.

```sh
./start.sh <person> <mode> <0-31> [<ip of bob>] [<port>]
```

where 0 stands for Alice and 1 stands for Bob in `person` arg. 

`c` for compare (x>=y) and `a` for addition (mod 32) in `mode` arg.

## references

- [混淆电路介绍（一）不经意传输](https://zhuanlan.zhihu.com/p/126396795)
- [GMW Protocol 介绍](https://zhuanlan.zhihu.com/p/237061306)
