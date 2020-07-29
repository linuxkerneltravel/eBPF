#### BPF接口(函数/宏)

| 函数                       | 功能                                                         |
| :------------------------- | :----------------------------------------------------------- |
| bpf_ktime_get_ns()         | 返回纳秒时间                                                 |
| BPF_HASH(last)             | 创建BPF映射对象，叫做last。如果没有指定任何参数，所以健值都是无符号64位 |
| bpf_trace_printk()         | 输出字符串，类似printf ,在调试中使用个，工具中使用BPF_PERF_OUTPUT() |
| bpf_get_current_pid_tgid() | 函数获得pid进程,其中低32位是进程ID,高32位是组id              |
| BPF_PERF_OUTPUT(events)    | 命名输出频道名字为events.                                    |
| bpf_get_current_common()   | 函数用当前进程名字填充第一个参数地址                         |
| events.perf_submit()       | 通过ring buffer将事件提交到用户层                            |

#### 接口描述

1. BPF_HASH 和 BPF_TABLE

   虽然BCC提供对内核导出的全部数据结构的访问，但最常用的两个是BPF_HASH和BPF_TABLE。

   从根本上讲，BCC的所有数据结构都是map，在它们之上构建更高级别的数据结构。其中最基本的是BPF_TABLE。

   BPF_TABLE宏接受一种类型的表(hash, percpu_array, or array)作为参数，以及其他宏，如BPF_HASH和BPF_ARRAY仅仅是围绕BPF_TABLE进行包装。

   因为所有的数据结构都是map，所以它们都支持相同的核心功能集，包括map.lookup()，map.update()，和map.delete()。也有一些map特定的功能，如map.perf_read()为BPF_PERF_ARRAY的功能，map.call()为BPF_PROG_ARRAY的功能。