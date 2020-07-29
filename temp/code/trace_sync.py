#!/usr/bin/env python
# coding=utf-8

from bcc import BPF

b = BPF(text = '''
        int kprobe__sys_sync(void *ctx) {
        /*BPF程序中声明的所有函数都希望在probe上运行
         *因此它们都需要将pt_reg* ctx作为i第一个参数
         *
         * 如果需要定义一些不会在probe上执行的辅助函数
         * 则需要用static inline来定义它们，以使编译器内联
         * 有时候还需要向其中添加_always_inline功能属性
         */
                bpf_trace_printk("sys_sync() called");

                return 0;
        }
        ''')

print 'Tracing sys_sync()...Ctrl-C to end'
while True:
    try:
        b.trace_print()
    except KeyboardInterrupt:
        exit()

