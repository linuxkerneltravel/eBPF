#!/usr/bin/env python
# coding=utf-8

#tracepoint比较稳定，如果可以都建议用tracepoint替代kprobes
#
#可以使用perf list命令来列出可用的tracepoints
#
#将eBPF程序附加到tracepoint上需要内核版本大于4.7
#
# TRACEPOINT_PROBE()宏：该宏声明要附加到跟踪点的函数，\
#                       每次触发该跟踪点时都会调用该函数
#  
#  以下的C代码片段显示了一个空的eBPF程序：该程序每次在内核中调用kmalloc()时运行
#               TRACEPOINT_PROBE(kmem, kmalloc) { 
#                       retrurn 0;
#               }
#               该宏的参数是跟踪点的类别和事件本身。    \
#               这将直接转换为debugfs文件系统的层次结构布局 \
#               (例如：/sys/kernel/debug/traceing/events/category/event)        
#

#程序功能：
#           跟踪随机读
from __future__ import print_function
from bcc import BPF

#load eBPF program
b = BPF(text = '''
        /*将eBPF程序附加到tracepoint上*/
        /*  TRACEPOINT_PROBE(random, urandon_read)  \
            是内核的tracepoint random:urandom_read. \
            其格式位于 /sys/kernel/debug/tracing/events/random/urandom_read/format
        */
        TRACEPOINT_PROBE(random, urandom_read) {
                bpf_trace_printk("%d\\n", args->got_bits);

                return 0;
        }
        ''')

#header
print("%-18s %-16s %-6s %s"%("TIME(s)", 
                             "COMM", "PID", "GOTBITS"))

#format output
while 1:
    try:
        (task, pid, cpu, flags, ts, msg) = b.trace_fields()
    except ValueError:
        continue
    print("%-18.9f %-16s %-6d %s"%(ts, task, pid, msg))
