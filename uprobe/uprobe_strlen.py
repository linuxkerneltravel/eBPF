#!/usr/bin/env python
# coding=utf-8

#程序功能：
#           跟踪用户层函数 strlen()
#
#跟踪用户层函数使用uprobe，对应的BPF函数是attach_uprobe
#           例如：
#                   b.attach_uprobe(name = "c", sym = "strlen", fn_name = "count")
#           含义：
#                   附加到C库，函数为strlen(),对应的处理函数为count

from __future__ import print_function
from bcc import BPF
from time import sleep

#load eBPF program
b = BPF(text = '''
        #include <uapi/linux/ptrace.h>

        struct key_t {
                char c[80];
        };
        
        BPF_HASH(counts, struct key_t);

        int count(struct pt_regs *ctx) {
                if (!PT_REGS_PARM1(ctx))
                        return 0;
                struct key_t key = {};
                u64 zero = 0, *val;

        bpf_probe_read(&key.c, sizeof(key.c), 
                        (void *)PT_REGS_PARM1(ctx));
        val = counts.lookup_or_init(&key, &zero);
        (*val)++;

        return 0;
        }
        ''')

b.attach_uprobe(name = "c", sym = "strlen", fn_name = "count")

#header
print("Tracing strlen()...Hit Ctrl-C to end.")

#sleep until Ctrl-C
try:
    sleep(99999999)
except KeyboardInterrupt:
    pass

#print output
print("%10s %s"%("COUNT", "STRING"))

counts = b.get_table("counts")

for k,v in sorted(counts.items(), key = lambda counts:counts[1].value):
    print("%10d\"%s\""%(v.value, k.c.encode('string-escape')))
