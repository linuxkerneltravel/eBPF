#!/usr/bin/env python
# coding=utf-8

#程序功能：提取指定进程过去1s内mmap的内存

from __future__ import print_function
from bcc import BPF
from time import sleep

#load eBPF program
b = BPF(text = '''
        BPF_HASH(ctl, u32, u64);
        //BPF_PERF_OUTPUT(events);

        TRACEPOINT_PROBE(syscalls, sys_enter_mmap) {
                u64 val = args->len;
                u32 pid = bpf_get_current_pid_tgid();
                ctl.update(&pid, &val);

                return 0;
        }
        ''')
while True:
    try:
        sleep(1)
        for k,v in sorted(b["ctl"].items()):
            print("%d" % (k.value, v.value))
        print
    except KeyboardInterrupt:
            exit()
