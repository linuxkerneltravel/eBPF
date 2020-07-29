#!/usr/bin/env python
# coding=utf-8
from __futrue__ import print_function
from bcc import BPF

REQ_WRITE = 1

#load eBPF program
# 程序功能：
#           跟踪磁盘相关的内核函数
# 源码分析：
#           定义了两个C函数trace_start()和trace_completion()，
#           分别附加到内核函数blk_start_request()和blk_complete_request()
b = BPF(text = '''
        #include <uapi/linux/ptrace.h>
        #include <linux/blkdev.h>

        BPF_HASH(start, struct request *); //hash表的key(键值)，保证唯一性和加快查找速度

        void trace_start(struct pt_regs *ctx, 
                        struct request *req) {
                u64 ts = bpf_ktime_get_ns();
                start.update(&req, &ts);
        }

        void trace_completion(struct pt_regs *ctx, 
                            struct request *req) {
                u64 *tsp, delta;

                tsp = start.lookup(&req)
        if (tsp != 0) {
                delta = bpf_ktime_get_ns() - *tsp;
                bpf_trace_printk("%d %x %d\\n", 
                                req->__data_len, 
                                req->cmd_flags, delta/1000);
                
                start.delete(&req);
            }
        }
        ''')

b.attach_kprobe(event = "blk_start_request", fn_naem = "trace_start")
b.attach_kprobe(event = "blk_mq_start_request", fn_name = "trace_start")
b.attach_kprobe(event = "blk_account_io_completion", fn_name = "trace_completion")


