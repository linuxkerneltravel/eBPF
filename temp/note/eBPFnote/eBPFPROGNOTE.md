### eBPF程序分析总结

参考资料：[eBPF简史](https://linux.cn/article-9032-1.html)

#### eBPF example

- sockex1_user.c

  ```c
  #include <…>
  // 篇幅所限，清单 3 和 4 都只罗列出部分关键代码，有兴趣一窥全貌的读者可以移步 http://elixir.free-electrons.com/linux/v4.12.6/source/samples/bpf深入学习
  int main(int ac, char **argv)
  {
      // 1. eBPF 的伪代码位于 sockex1_kern.o 中，这是一个由 llvm 生成的 elf 格式文件，指令集为 bpf;
      snprintf(filename, sizeof(filename), "%s_kern.o", argv[0]);
      if (load_bpf_file(filename)) {
          // load_bpf_file()定义于 bpf_load.c，利用 libelf 来解析 sockex1_kern.o
          // 并利用 bpf_load_program 将解析出的伪代码 attach 进内核;
      }
      // 2. 因为 sockex1_kern.o 中 bpf 程序的类型为 BPF_PROG_TYPE_SOCKET_FILTER
      // 所以这里需要用用 SO_ATTACH_BPF 来指明程序的 sk_filter 要挂载到哪一个套接字上
      sock = open_raw_sock("lo");
      assert(setsockopt(sock, SOL_SOCKET, SO_ATTACH_BPF, prog_fd,
      sizeof(prog_fd[0])) == 0);
      //……
      for (i = 0; i < 5; i++) {
          // 3. 利用 map 机制获取经由 lo 发出的 tcp 报文的总长度
          key = IPPROTO_TCP;
          assert(bpf_map_lookup_elem(map_fd[0], &key, &tcp_cnt) == 0);
          // ……
      }
      return 0;
  }
  ```

- sockex1_kern.c

  ```c
  #include <……>
  // 预先定义好的 map 对象
  // 这里要注意好其实 map 是需要由用户空间程序调用 bpf_create_map()进行创建的
  // 在这里定义的 map 对象，实际上会在 load_bpf_file()解析 ELF 文件的同时被解析和创建出来
  // 这里的 SEC(NAME)宏表示在当前 obj 文件中新增一个段(section)
  struct bpf_map_def SEC("maps") my_map = {
      .type = BPF_MAP_TYPE_ARRAY,
      .key_size = sizeof(u32),
      .value_size = sizeof(long),
      .max_entries = 256,
  };
  SEC("socket1")
  int bpf_prog1(struct __sk_buff *skb)
  {
      // 这个例子比较简单，仅仅是读取输入报文的包头中的协议位而已
      // 这里的 load_byte 实际指向了 llvm 的 built-in 函数 asm(llvm.bpf.load.byte)
      // 用于生成 eBPF 指令 BPF_LD_ABS 和 BPF_LD_IND
      int index = load_byte(skb, ETH_HLEN + offsetof(struct iphdr, protocol));
      long *value;
      // ……
      // 根据 key(&index，注意这是一个指向函数的引用)获取对应的 value
      value = bpf_map_lookup_elem(&my_map, &index);
      if (value)
          __sync_fetch_and_add(value, skb->len); //这里的__sync_fetch_and_add 是 llvm 中的内嵌函数，表示 atomic 加操作
      return 0;
  }
  // 为了满足 GPL 毒药的需求，所有会注入内核的 BPF 代码都须显式的支持 GPL 协议
  char _license[] SEC("license") = "GPL";
  ```

- 总结

  ![eBPF程序原理](/temp/note/eBPFnote/image/eBPF程序原理.png)

