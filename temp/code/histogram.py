#!/usr/bin/env python
# coding=utf-8

#直方图练习
from bcc import BPF
from time import sleep

#load eBPF program
b = BPF(text = '''
        #include <uapi/linux/ptrace.h>
        #include <linux/blkdev.h>

        /*直方图(histogram)*/
        BPF_HISTOGRAM(dist);    //BPF_HISTOGRAM(dist)定义BPF直方图映射对象，名字叫做dist

        /*把kprobe插在blk_account_io_completion()上*/
        int kprobe__blk_account_io_completion(struct pt_regs *ctx, 
                                                struct request *req) {
                //dist.increment()函数会增加直方图中各个值，值由参数指定。increment:增量
                dist.increment(bpf_log2l(req->__data_len/1024)); //bpf_log2l()将值变成log-2模式

                return 0;
        }
        ''')

#header
print("Tracing ...Hit Ctrl-C to end.") #python的print的会自动换行，不需要\n

#trace until Ctrl-C
try:
    sleep(99999999)
except KeyboardInterrupt:
    print

#output
b["dist"].print_log2_hist("kbytes") #print_log2_hist("kbytes")打印hist直方图，列单位为kbytes
