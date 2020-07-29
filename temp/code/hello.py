#!/usr/bin/env python
# coding=utf-8

from bcc import BPF
#从bcc package中导入BPF类，BPF是基类
# 通过BPF()来实例化一个对象，这个对象就是eBPF程序。
# BPF()实例化对象的时候，会调用叫做__init__(self)的构造函数
#bcc是一个python的package,路径如下：
#   /usr/lib/python2.7/dist-packages/bcc
#python的package一个典型的特征就是在package中一定有一个__init__.py的模块。

#ebpf program
# 整个eBPF程序都包含在program变量中，这是在
# eBPF虚拟机上的内核中运行的代码
program = '''
/*
 *kprobe__前缀指示bcc工具链将kprobe附加到   \   
 *其后的内核符号上
 *
 *将探针(uprobe,kprobe,tracepoints或USDT)   \
 *插入到给定的函数sys_cone()中，该函数可以  \
 *在内核中或在用户空间代码中
 *
 *使用kprobe的语法是:                       \
 *          kprobe__kernel_function_name    \
 *其中kprobe__是前缀，用于给内核函数创建    \
 *一个kprobe(内核函数调用的动态跟踪)。
 *
 *也可通过C语言函数定义一个C函数，然后使用  \
 *python的BPF.attach_kprobe()来关联到内核函数
 *
 *  kretprobes:                             \
 *              kretprobes动态跟踪内核函数的返回，语法如下：    \
 *              kretprobe__kernel_function_name                 \
 *              前缀是kretprobe__。也可以使用python的
 *              BPF.attach_kretprobe()来关联Ｃ函数到内核函数。  \
 *  
 *  例子:   int kretprobe__tcp_v4_connect(struct pt_regs *ctx)
 *          {
 *                  int ret = PT_REGS_RC(ctx);  //返回值保存在ret中
 *                          [...]
 *          }
 */

int kprobe__sys_clone(void *ctx) //kprobe__是前缀，用于给内核函数创建一个kprobe
{                                //ctx有参数，但是由于我们不在这里使用它们，因此我们将其转换为void *
    //当调用sys_clone并触发该kprobe时，eBPF程序运行
    //bpf_trace_printk()打印“hello world”到内核的trace buffer(跟踪缓冲区)。
    //kernel trace buffer就是/sys/kernel/debug/tracing/trace_pipe
    
    bpf_trace_printk("hello, world!\\n");
    //bpf_trace_printk()使用类似“追加写入”的方式向trace_pipe文件写入字符串内容
    //可以使用trace_print(fmt = '{number}')的方式单独读取bpf_trace_printk()写入的内容

    return 0;   //return 0是必要的，不同的内核挂钩点会根据return的值，作不同的处理。如果为定义  \
                //返回值，可能会导致奇怪的性能表现。
}
'''

#load eBPF program
#python程序的其余部分将eBPF代码加载到内核并运行
b = BPF(text = program) #实例化一个新的BPF对象b

#BPF_trace_print()对内核的trace buffer(/sys/kerel/debug/tracing/trace_pipe)执行阻塞读取
# 并将内容打印到标准输出中
b.trace_print() #trace_print()是BPF的python库的接口

#以前将程序编译为eBPF字节码并将其加载到内核的繁琐任务完全是通过实例化一个新的BPF对象来完成的
# 所有的底层工作都在幕后，由python绑定和bcc的libbpf完成
# libbpf是BPF加载器。libbpf在运行时获取之前已经编译好的BPF ELF文件，然后针对运行平台做进一步的处理，并触发BPF程序的加载和验证
