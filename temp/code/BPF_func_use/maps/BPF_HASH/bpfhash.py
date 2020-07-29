#!/usr/bin/env python
# coding=utf-8


#analyze disksnoop.py

from __future__ import print_function
from bcc import BPF
'''
printb(s)

print a bytes object to stdout and flush
'''
from bcc.utils import printb

REQ_WRITE = 1

b = BPF(text = '''
        /*
         *定义寄存器组的结构体：struct pt_regs
         * 内核路径：/arch/x86/include/uapi/asm/ptrace.h
         * eBPF使用bpf_load_program()函数来将BPF代码载入内核
         * bpf_load_program()负责通过参数向内核提供三类信息：
         *      .BPF程序的类型
         *      .BPF代码
         *      .代码运行时所需要的存放log的缓存地址(位于用户空间)
         * 通过bpf_load_program()的参数bpf_prog_type，可以看到eBPF支持的程序类型
         *      bpf_prog_type：     BPF_PROG_TYPE_KPROBE
         *      BPF prog入口参数：  struct pt_regs
         *      程序类型：          用于kprobe功能的BPF代码
         */
        #include <uapi/linux/ptrace.h>  

        //定义了内核数据结构：struct request
        // 内核路径：/include/linux/blkdev.h
        #include <linux/blkdev.h>

        //define hash table name:start
        //define key pointer type:struct request *
        BPF_HASH(start, struct request *);
        //在hash table中使用指向struct request的指针作为key，这在跟踪中很常见
        //指向结构体的指针是很好的key，因为它们是唯一的：两个结构体不能有相同的指针地址。
        //存储时间戳有两个常用的key：指向结构体的指针，和线程id。

        /* define probe_1 */
        /*
         *two arguments:ctx point to registers context
         *              req is key pointer,point to 'struct request'
         */
        //开始的时候触发
        void trace_start(struct pt_regs *ctx, struct request *req) {
                //struct pt_regs *ctx用于寄存器和BPF上下文
                //stroed start timestamp 
                u64 ts = bpf_ktime_get_ns();

                //update timestamp 
                start.update(&req, &ts);//用后面的覆写以前的值
        }

        /* define probe_2 */
        //完成的时候触发
        void trace_completion(struct pt_regs *ctx, struct request *req) {
                u64 *tsp, delta;

                //return a pointer to its value if it exists,else NULL
                tsp = start.lookup(&req);
                if (tsp) {
                        //u64 bpf_ktime_get_ns(void)
                        delta = bpf_ktime_get_ns() - *tsp;

                        /* struct request {
                         *          ...
                         *          unsigned int cmd_flags;
                         *          ...
                         *          unsigned int __data_len;
                         *          ...
                         * };
                         */
                        bpf_trace_printk("%d %x %d\\n", 
                                            req->__data_len, 
                                            req->cmd_flags, 
                                            delta / 1000);
                        //__data_len，cmd_flags, delta/1000这三个数据会以类似追加的方式写在trace_pipe文件的末尾。
                        //注意bpf_trace_printk()的打印格式，3个数据之间是由空格分隔，这对于python后期的处理有用
                        //python会用trace_fields()读取trace_pipe的每个字段，上述的三个字段以对象的形式存在，python会用msg指向这三个数据
                        //然后单独拿出来msg使用split()进行切片
                        //切片后会生成一个包含3个字符串的list
                        //最后用一个三元组来保存这个list里的数据。
                        //其中，每个元组对应保存一个list中的字符串。

                        start.delete(&req); //delete key
                }
        }
        ''')

#call class BPF's method:get_kprobe_functions
#因为get_kprobe_functions()是BPF类的静态方法
if BPF.get_kprobe_functions(b'blk_start_request'):
#开头的b表示这是一个bytes类型，即字节流类型。
#pythn2将string处理为原生的bytes类型，而不是unicode。
#pyhon3所有的string均是unicode类型。
#python3.x里默认的str是(python2.x里的)unicode。bytes是(python2.x)的str
#b""或者b''前缀代表的就是bytes.
#b'blk_start_request'中的b前缀在python2.x里没有什么具体意义，只是为了兼容python3.c的这种写法
    b.attach_kprobe(event = 'blk_start_request', 
                              fn_name = 'trace_start')

b.attach_kprobe(event = 'blk_mq_start_request', fn_name = 'trace_start')
b.attach_kprobe(event = 'blk_account_io_completion', 
                              fn_name = 'trace_completion')

#header
#-号左对齐，+号右对齐(默认不用写出+号)
print('%-18s %-2s %-7s %8s' % ('TIME(s)', 'T', 'BYTES', 'LAT(ms)'))

#format output
while True:
    try:
        (task, pid, cpu, flags, ts, msg) = b.trace_fields()
        #split()以空字符(包含空格，换行\n，制表符\t)对字符串进行切片
        #msg指向number对象，然后调用number的split()方法
        (bytes_s, bflags_s, us_s) = msg.split()
        #(bytes_s,bflags_s,us_s)是一个元组
        #这个元组用来接收切片后的返回值。

        #int():将一个字符串或数字转换为整型
        #int(x, base=10):x表示字符串或数字，base表示进制数，默认十进制
        #int(3.6) = 3
        #int('12', 16)：如果是带着参数base的话，12要以字符串的形式
        # 进行输入
        if int(bflags_s, 16) & REQ_WRITE:   #将16进制的bflags_s转换为十进制数
            type_s = b'W'
        elif bytes_s == '0':#see blk_fill_rwbs() for logic
            type_s = b'M'
        else:
            type_s = b'R'
        ms = float(int(us_s, 10)) / 1000

        #print(b'%-18.9f %-2s %-7s %8.2f' % (ts, type_s, bytes_s, ms))
        printb(b'%-18.9f %-2s %-7s %8.2f' % (ts, type_s, bytes_s, ms))
    except KeyboardInterrupt:
        exit()
