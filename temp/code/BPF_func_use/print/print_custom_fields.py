#!/usr/bin/env python
# coding=utf-8

#this is a exercise to print custom fields

from __future__ import print_function #必须放第一个
from bcc import BPF #从bcc package中导入BPF类

b = BPF(text = '''
        int hello(void *ctx) {
                bpf_trace_printk("hello, world\\n");

                return 0;
        }
        ''')

b.attach_kprobe(event = b.get_syscall_fnname('clone'), 
                fn_name = 'hello')

print('PID MESSAGE')
try:
    #b.trace_print() #原样打印trace_pipe的输出。print trace_pipe output as-is
    #通过指定tuple的index，有选择的打印信息
    b.trace_print(fmt = '{0} {5}')  #{0}{5}是tuple的index，打印时中间用一个空格分隔
except KeyboardInterrupt:
    exit()
