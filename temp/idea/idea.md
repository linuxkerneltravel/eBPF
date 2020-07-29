### idea

记录一些eBPF/BCC编程中的思考和心得

#### eBPF程序

1. 一触即发

   今天在分析一个eBPF程序结构的时候，想到eBPF程序它和普通的用户程序有两点不同(目前就想到这两点)。

   第一个，eBPF程序是用户态的代码，但可以在内核空间执行。这也是BPF/eBPF机制的一个亮点，让用户程序具有在内核空间执行的能力，但这也对用户程序的安全性有较为严格的检查，因为内核一定要能发现用户代码的潜在隐患。

   第二个。用户程序一般都是运行一次，或者根据我们的需求来运行，直白一点，就是我让你运行你才运行。而eBPF程序的运行带有种自动化的行为。eBPF程序的特点就是为了追踪一个事件，或者说跟踪一个函数，比如kmalloc()，在某一段时间内，kmalloc()可能会被调用5次，相应的eBPF程序也会被执行5次。所以eBPF程序的运行特点是一触即发，随触随发的形式。普通的用户程序的执行概括的说就是：执行->结束，而eBPF程序的情况是：执行->执行->执行-> …… ->执行->结束，而且eBPF程序每次执行，都是完全相同的代码再走一遍。

2. 循环

   目前看着教程练习了一些eBPF程序，发现BCC例子中的很多eBPF程序里看不到有循环。猜测eBPF程序里应该不能写循环。打算写个例子来验证下。

   +++++++++++++++++++++++++++++++++时间分割线+++++++++++++++++++++++++++++++++++++++

   经过验证，eBPF程序中可以使用循环。但是循环次数必须是确定的值，如果是死循环，比如for(;;)，运行就会失败。

   **代码1：有限的循环5次**

   ```python
   #!/usr/bin/env python
   # coding=utf-8
   
   from bcc import BPF
   
   b = BPF(text = '''
           int kprobe__sys_clone(void *ctx) {
                   int i = 0;
                   for (i; i < 5; i++)  
                           bpf_trace_printk("hello world\\n");
   
                   return 0;
           }
           ''')
   
   b.trace_print()
   
   ```

   运行结果：

   ```shell
   $ sudo python ./for_limited.py
   
   	ThreadPoolForeg-7898  [001] .... 288815.687851: 0: hello world
    	ThreadPoolForeg-7898  [001] .... 288815.687910: 0: hello world
    	ThreadPoolForeg-7898  [001] .... 288815.687912: 0: hello world
    	ThreadPoolForeg-7898  [001] .... 288815.687912: 0: hello world
    	ThreadPoolForeg-7898  [001] .... 288815.687913: 0: hello world
    ManagementAgent-1405  [003] .... 288827.365195: 0: hello world
    ManagementAgent-1405  [003] .... 288827.365241: 0: hello world
    ManagementAgent-1405  [003] .... 288827.365242: 0: hello world
    ManagementAgent-1405  [003] .... 288827.365243: 0: hello world
    ManagementAgent-1405  [003] .... 288827.365243: 0: hello world
    ...
   
   ```

   代码2：在eBPF程序中写入无限循环

   ```python
   #!/usr/bin/env python
   # coding=utf-8
   
   from bcc import BPF
   
   b = BPF(text = '''
           int kprobe__sys_clone(void *ctx) {
                   for (;;)  
                           bpf_trace_printk("hello world\\n");
   
                   return 0;
           }
           ''')
   
   b.trace_print()
   
   ```

   运行结果：

   ```shell
   $ sudo python ./for_unlimited.py
   
   bpf: Failed to load program: Invalid argument
   ```

   