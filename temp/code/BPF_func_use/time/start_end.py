#!/usr/bin/env python
# coding=utf-8

from __future__ import print_function
from bcc import BPF 

b = BPF(text = '''
        #include <uapi/linux/ptrace.h>

        BPF_HASH(last);

        int do_trace(struct pt_regs *ctx) {
                u64 ts, *tsp, delta, key = 0;   
                // *val map.lookup(&key)
                //lookup()函数在map中查找key，如果存在就返回
                //指向其值的指针，否则返回NULL

                //尝试读取存储的时间戳
                //attempt to read stored timestamp
                tsp = last.lookup(&key);
                if (tsp != NULL) {
                        delta = bpf_ktime_get_ns() - *tsp;
                        //u64 bpf_ktime_get_ns(void)
                        //返回值，当前时间(以纳秒位单位)

                        if (delta < 1000000000) {
                                //output if time is less than 1 second
                                bpf_trace_printk("%d\\n", delta / 1000000000);
                        }
                        
                        last.delete(&key);
                }
                
                bpf_trace_printk("%d", key);
                //update stored timestamp
                ts = bpf_ktime_get_ns();
                last.update(&key, &ts);
                //map.update(&key, &value)
                //将第二个参数中的值与键相关联，覆盖以前的任何值

                return 0;
        }
        ''')

b.attach_kprobe(event = b.get_syscall_fnname('mmap'), 
                                    fn_name = 'do_trace')

print ('Tracing for quick sync`s...Ctrl-C to end ')

#format output
start = 0   #global variable
while 1:
    #下面这语句是固定的，按照这个格式用就ok
    #trace_fields()的作用就是从trace_pipe文件中读取一行
    #然后将其作为字段返回
    (task, pid, cpu, flags, ts, ms) = b.trace_fields()
    #ms的值来自于BPF program中由bpf_trace_printk()“追加”
    #写入到trace_pipe中的delta
    if start == 0:
        start = ts  #ts是trace_fields()读出来的
    ts = ts - start
    print('At time %.2fs:mutiple syncs detectd, last %s ms ago' % (ts, ms))
    #%.2fs中，f表示float，s表示输出的数字后面带s





