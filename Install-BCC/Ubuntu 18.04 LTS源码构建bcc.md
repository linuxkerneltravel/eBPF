### Ubuntu 18.04 LTS源码构建bcc

目前安装bcc有两种方式，一种是直接使用发行版提供的软件包，Ubuntu里叫bpfcc-tools，CentOS7中的是bcc-tools。另一种方式是源码编译安装。推荐通过源码编译安装。

> 第一种和第二种方式只能二选一，否则会有冲突导致不可用

有人反应第一种方式安装bcc后，BPF模块各种出错。目前通过源码编译安装是最稳定最安全的方法。下面将详细介绍通过源码编译安装bcc。

#### 踩坑指南

- Linux发行版最好用Ubuntu，不要用CentOS7
- 尽量不要用曾经手动升级过内核的系统，用原生的发行版系统
- 命令安装与源码安装只可二选一，否则可能导致不可用
- 不要直接clone官方仓库，编译会缺文件，使用bcc的release包。
- 官方要求的依赖缺少对python3附加模块的支持，需要自己手动添加

#### 源码编译安装bcc

1. 检查环境(特别高版本内核可以忽略此步)

   **内核配置**：高版本的内核这些是标配，基本不用管，不放心也可以检查下。通过命令

   ```c
   less /boot/config-<kernel-version>
   ```

   配置选项

   ```c
   CONFIG_BPF=y
   CONFIG_BPF_SYSCALL=y
   # [optional, for tc filters]
   CONFIG_NET_CLS_BPF=m
   # [optional, for tc actions]
   CONFIG_NET_ACT_BPF=m
   CONFIG_BPF_JIT=y
   # [for Linux kernel versions 4.1 through 4.6]
   CONFIG_HAVE_BPF_JIT=y
   # [for Linux kernel versions 4.7 and later]
   CONFIG_HAVE_EBPF_JIT=y
   # [optional, for kprobes]
   CONFIG_BPF_EVENTS=y
   ```

   ```c
   CONFIG_NET_SCH_SFQ=m
   CONFIG_NET_ACT_POLICE=m
   CONFIG_NET_ACT_GACT=m
   CONFIG_DUMMY=m
   CONFIG_VXLAN=m
   ```

   **构建工具**：这些是构建依赖的工具，和它们最低的版本要求(后面会安装，这里用于查看版本)

   ![工具检查](C:\Users\hds\Desktop\工具检查.png)

2. 正式安装

   先安装所有依赖的工具

   ```c
   sudo apt-get -y install bison build-essential cmake flex git libedit-dev \
     libllvm6.0 llvm-6.0-dev libclang-6.0-dev python zlib1g-dev libelf-dev
   ```

   除了官网要求的这些工具之外，还要额外安装几个python3的包

   ```c
   sudo apt-get install python3-distutils
   sudo apt-get install python3-pip
   sudo apt-get install python3-setuptools
   ```

   > 虽然官网没有要求安装，但我在实际编译过程中发生编译中断，通过查资料发现是缺少python3的依赖包。Python基本解释器确实需要一些附加模块，这些未默认安装在Ubuntu 18.04

   接下来在主目录新建一个文件夹，用来放bcc源码

   ```c
   mkdir ebpf; cd ebpf
   ```

   下载bcc的release包：[点击下载](https://github.com/iovisor/bcc/releases)

   ![release包](C:\Users\hds\Desktop\release包.png)

   选择<u>**bcc-src-with-submodule.tar.gz**</u>，然后解压。剩下的只要依次执行下列命令就可以安装成功了。

   ```c
   mkdir bcc/build; cd bcc/build
   cmake ..
   make
   sudo make install
   cmake -DPYTHON_CMD=python3 .. # build python3 binding
   pushd src/python/
   make
   sudo make install
   popd
   ```

   3. 使用bcc tools里的工具

      > bcc工具的默认安装目录为/usr/share/bcc/tools

      使用cachestat查看缓存命中情况

      ![bcc工具2](C:\Users\hds\Desktop\bcc工具2.png)

      运行一个最简单的ebpf程序：检测到`clone`系统调用就打印`hello world`

      ![bcc工具1](C:\Users\hds\Desktop\bcc工具1.png)

