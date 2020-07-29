#!/usr/bin/env python
# coding=utf-8

from bcc import BPF 

b = BPF(text = '''
        #include <uapi/linux/ptrace.h>

        //BPF_HASH(name[,key_type[,leaf_type[,size]]])
        //defaults:BPF_HASH(name, key_type=u64, leaf_type=u64, size=10240)
        BPF_HASH(event);
        //event是hash table的名字。
        //event后，没有别的参数。表示key的类型采用默认的u64。
        //if need to modify the key type, set as:struct request*
        //means that key has new type, new type is 'struct request*'
        //remember key is a pointer!!!

        int kprobe__sys_clone(void *ctx) {
                u64 key = 0;
                u64 count = 0;
                u64 *val_ptr;
                
        bpf_trace_printk("first key value:%llu count:%d\\n", key, count);

                val_ptr = event.lookup(&key);
                if (val_ptr) {
                        count++;
                        event.delete(&key);
        bpf_trace_printk("after delete key value:%llu count:%d\\n", key, count);
                }

        event.update(&key, &count); //修改变量的值要通过引用传递，&variable_name
        
        bpf_trace_printk("after update key value:%llu count:%d\\n", key, count);

        return 0;
        }
        ''')

#b.trace_print(fmt = '{5}')
b.trace_print()
