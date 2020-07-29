#!/usr/bin/env python
# coding=utf-8

from bcc import BPF

b = BPF(text = '''
        BPF_HASH(callers, u64, unsigned long);

        /*TRACEPOINT_PROBE()的参数是跟踪点的类别和事件本身  \
         * 跟踪点的类别在/sys/kernel/debug/tracing/events文件夹下   \
         * vmscan是events里的一个类别，mm_vmscan_writepage()是vmscan/里的事件   \
         * TRACEPOINT_PROBE()会将跟踪点的类别和事件直接转换为debugfs文件系统的层次结构布局
         */
        TRACEPOINT_PROBE(vmscan, mm_vmscan_writepage) {
                bpf_trace_printk("hello world\\n");     /*bpf_trace_printk()用于从BPF程序写入/sys/kernel/debug/tracing/trace_pipe
                                                         * 然后可以使用BPF.trace_print()函数在python中打印这些消息
                                                         *
                                                         *bpf_trace_printk()的主要缺点是，由于trace_pipe文件是全局自愿，因此它
                                                         * 包含由并发编写器编写的所有消息，因此很难从单个BPF程序中过滤消息。
                                                         *
                                                         *首选方法是将消息存储在BPF程序内的BPF_PERF_OUTPUT map中，然后使用
                                                         * open_perf_buffer()和kprobe_poll()处理它们。
                return 0;
        }
        ''')

b.trace_print()
