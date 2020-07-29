#!/usr/bin/env python
# coding=utf-8

#验证eBPF程序是否允许循环
# 结果：eBPF程序可以写循环。如果循环次数是确定的，程序可以运行。    \
#       如果是死循环，如for(;;)，程序不能运行。

from bcc import BPF

b = BPF(text = '''
        int kprobe__sys_clone(void *ctx) {
                int i = 0;
                for (i; i < 5; i++)  
                        bpf_trace_printk("hello world\\n");

                return 0;
        }
        ''')

b.trace_print()
