#!/usr/bin/env python
# coding=utf-8

#USDT在python中有支持

USDT(pid = int(pid))    #初始化指定进程的USDT

#绑定BPF的C函数到http_server_request的USDT probe
u.enable_probe(probe = "http_server_request", fn_name = "do_trace")

#传递USDT对象到BPF中
BPF(text = bpf_text, usdt_contexts = [u])
