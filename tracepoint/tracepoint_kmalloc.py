#!/usr/bin/env python
# coding=utf-8

#程序功能：使用BPF_HASH map存储kmalloc()调用点的内核指令指针地址，和调用次数
# 并使用python进行后期的处理

from bcc import BPF
from time import sleep

#eBPF program
b = BPF(text = '''
        /*
         *BPF_HASH()宏带有许多可选参数,     \
         * 但是对于大多数用途，需要指定的只是此     \
         * 哈希表实例的名称(本例中为callers)，键数据类型(u64)，值数据类型(unsigned long)
         */
        BPF_HASH(callers, u64, unsigned long);  //一旦计数存储在哈希表中，就可以使用python处理该计数
                                                //通过索引BPF对象(实例中的b)来完成对该表的访问
        TRACEPOINT_PROBE(kmem, kmalloc) {
                //向跟踪点传递参数
                //在eBPF程序中，可以通过magic args变量访问tracepoint参数
                u64 ip = args->call_site;   //kmalloc()调用的内核指令地址
                unsigned long *count;
                unsigned long c = 1;

                count = callers.lookup((u64 *)&ip); //使用lookup()函数访问BPF哈希表条目；如果给定键值不存在任何条目，则返回NULL
                if (count != 0) 
                        c += *count;
                
                callers.update(&ip, &c);    //map.update()函数会插入一个新的key值(如果不存在)，或更新现有键的值

                return 0;
        }
        ''')

while True:
    try:
        sleep(1)
        #遍历callers哈希表中的所有项
        for k,v in sorted(b["callers"].items()):    #生成的python对象是HashTable(在BCC Python前端中定义)，
                                                    # 并可以使用items()函数访问其项
            print("%s %u" % (b.ksym(k.value), v.value)) #使用BCC的BPF.ksym()函数将内核地址转换为符号
        print
    except KeyboardInterrupt:
        exit()
