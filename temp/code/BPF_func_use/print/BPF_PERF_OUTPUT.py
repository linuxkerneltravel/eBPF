#!/usr/bin/env python
# coding=utf-8

#BPF_PERF_OUTPUT()
# 通过perf ring buffer创建BPF表，将定义的事件数据输出。
# 这个是将数据推送到用户态的建议方法
#
#perf_submit:
#       函数原型：int perf_submit((void *)ctx, (void *)data, u32 data_size)
#       该函数是BPF_PERF_OUTPUT表(即events)的方法，将定义的事件数据推送到用户态

from bcc import BPF

#load eBPF program
b = BPF(text = '''
        #include <linux/types.h>

        struct data_t {
                u32 pid;
                u64 ts;
                char comm[TASK_COMM_LEN];
        };

        BPF_PERF_OUTPUT(events);    //定义了一张输出表events

        int hello(struct pt_regs *ctx) {
                struct data_t data = {};
                data.pid = bpf_get_current_pid_tgid();
                data.ts = bpf_ktime_ns();
                bpf_get_current_comm(&data.comm, 
                                        sizeof(data.comm));

                /*代码中的输出表是events，数据通过events.perf_submit来推送*/
                events.perf_submit(ctx, &data, 
                                        sizeof(data));   //向BPF表推送数据

                return 0;
        }
        ''')
