#!/usr/bin/env python
# coding=utf-8
from bcc import BPF

#ebpf program
program = '''
int hello(void *ctx)
{
    bpf_trace_printk("hello, world!\\n");

    return 0;
}
'''

#load ebpf program
b = BPF(text = program)

#使用attach_kprobe()来创建sys_clone的kprobe,当触发时候运行hello程序
#可以调用多个attach_kprobe()来附加C程序给多个内核函数
b.attach_kprobe(event = b.get_syscall_fnname("clone"), fn_name = "hello")

print("%-18s %-16s %-6s %s"%("TIME(s)", "COMM", "PID", "MESSAGE"))

#output
while 1:
    try:
     (task, pid, cpu, flags, ts, msg) = b.trace_fields() #trace_fields()来返回来自trace_pipe的一组域
                                                         # 真正的工具应使用BPF_PERF_OUTPUT()
    except ValueError:
     continue
    print("%-18.9f %-16s %-6d %s"%(ts, task, pid, msg))
