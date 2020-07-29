#!/usr/bin/env python
# coding=utf-8

from bcc import BPF 

b = BPF(text = '''
        int hello(void *ctx) {
                bpf_trace_printk("hello, world\\n");

                return 0;
        }
        ''')

b.attach_kprobe(event = b.get_syscall_fnname('clone'), 
                fn_name = 'hello')

#print header
print '%-18s %-16s %-6s %s' %   \
        ('TIME(s)', 'COMM', 'PID', 'MESSAGE')
#下面的两种打印方式与上面的效果一样
#print ('%-18s %-16s %-6s %s' % 
#       ('TIME(s)', 'COMM', 'PID', 'MESSAGE'))

#print('%-18s %-16s %-6s %s' % 
#       ('TIME(s)', 'COMM', 'PID', 'MESSAGE'))

#format output
while 1:
    try:
        (task, pid, cpu, flags, ts, msg) = b.trace_fields()
        #前5个(task, pid, cpu, flags, ts)是trace_pipe默认有的
        #第6个开始，是bpf_trace_printk()以类似追加的方式写入trace_pipe的
    except ValueError:
        continue
    #print '%-18.9f %-16s %-6d %s' % (ts, task, pid, msg)
#-号表示左对齐，18.9中的18表示占18个空格的长度，9表示小数点后保留9位
    print '%-18.9f %-16s %-6d %s %-6d' % (ts, task, pid, msg, cpu)
