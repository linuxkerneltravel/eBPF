### bcc python

bcc的python相关的知识

#### 一.初始化

1. BPF

   语法：BPF({text = BPF_program | src_file = filename}, [usdt_contexts = [USDT_object, ...]])

   创建一个BPF对象，或者说实例化一个BPF对象，能通过交互来产生输出。

2. USDT

   语法：USDT({pid = pid | path = path})

   创建对象来使用USDT，可以指定进程ID，路径。

#### 二.事件

1. attach_kprobe

   语法：BPF.attach_kprobe(event = "event", fn_name = "name")

   使用内核动态跟踪的函数入口，关联C函数name和内核函数event()。

2. attach_kretprobe

   语法：BPF.attach_kretprobe(event = "event", fn_name = "name")

   关联C函数name和内核函数event，在内核函数返回的时候调用函数name。

3. attach_tracepoint

   语法：BPF.attach_tracepoint(tp = "tracepoint", fn_name = "name")

   关联C语言的定义的BPF函数和内核的tracepoint。也可以使用TRACEPOINT_PROBE宏，使用该宏可以使用高级的自声明的args结构体，args包含了tracepoint参数。如果使用attach_tracepoint，参数需要在BPF程序中声明。

4. attach_uprobe

   语法：BPF.attach_uprobe(name = "location", sym = "symbol", fn_name = "name")

   将在location中的函数事件symbol，关联到C定义的函数。当symbol调用时候回调用name函数。

   例如：

   ```python
   b.attach_uprobe(name = "c", sym = "strlen", fn_name = "count")
   ```

   表示将C库的函数strlen()与定义的C函数count关联，当strlen()被调用的时候，会执行C函数。

5. attach_uretprobe

   语法：BPF.attach_uretprobe(name = "location", sym = "symbol", fn_name = "name")

   同attach_uprobe一样，不过是在函数返回的时候调用name函数。

6. USDT.enable_probe

   语法：USDT.enable_probe(probe = probe, fn_name = name)

   将BPF的C函数附加到USDT探针上。

   例如：

   ```python
   u = USDT(pid = int(pid))
   u.enable_probe(probe = "http_server_request",  fn_name = "do_trace")
   ```

   查看二进制文件是否有USDT探针，可以使用如下命令检测stap调试段：

   ```shell
   #readelf -n binary
   ```

#### 三.调试输出

1. trace_print

   语法：BPF.trace_print(fmt = "fields")

   持续读取全局共享的/sys/kernel/debug/tracing/trace_pipe文件并输出。这个文件可以被BPF和bpf_trace_printk()函数写入。

   例如：

   ```python
   #print trace_pipe output as-is:
   b.trace_print()
   #print PID and message
   b.trace_print(fmt = "{1} {5}")
   ```

2. trace_fields

   语法：BPF.trace_fields(nonblocking = False)

   从全局共享文件/sys/kernel/debug/tracing/trace_pipe中读取一行并返回域。参数表示在等待写入的时候是否blocking。

#### 四.映射

1. print_log2_hist

   语法：table.print_log2_hist(val_type = "value", section_header = "Bucket ptr", section_print_fn = None)

   使用ASCII以log2直方图打印表。表必须用log2方式存储，这个可以通过bpf_log2()。

   val_type是可选的，表示列头。

   section_header：如果直方图有第二个键，多个表会被打印，section_header会被作为头描述。

   如果section_print_fn不是none，传递bucket值。

#### 五.关于BPF Errors

BPF中所有内存读取都要通过bpf_probe_read()函数将内存复制到BPF栈。如果直接读取内存，会出现Invalid mem access。