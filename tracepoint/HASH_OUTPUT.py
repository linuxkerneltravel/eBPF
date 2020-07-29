#!/usr/bin/env python
# coding=utf-8


bpf_text = """
#include <uapi/linux/ptrace.h>
#include <linux/sched.h>

struct val_t {
   u64 pid;
   int sig;
   int tpid;
   char comm[TASK_COMM_LEN];
};

struct data_t {
   u64 pid;
   int tpid;
   int sig;
   int ret;
   char comm[TASK_COMM_LEN];
};

BPF_HASH(infotmp, u32, struct val_t);
BPF_PERF_OUTPUT(events);

int syscall__kill(struct pt_regs *ctx, int tpid, int sig)
{
	u32 pid = bpf_get_current_pid_tgid();
	FILTER

	struct val_t val = {.pid = pid};
	if (bpf_get_current_comm(&val.comm, sizeof(val.comm)) == 0) {
    	val.tpid = tpid;
    	val.sig = sig;
    	infotmp.update(&pid, &val);
	}

	return 0;
};

int do_ret_sys_kill(struct pt_regs *ctx)
{
	struct data_t data = {};
	struct val_t *valp;
	u32 pid = bpf_get_current_pid_tgid();

	valp = infotmp.lookup(&pid);
	if (valp == 0) {
    	// missed entry
    	return 0;
	}

	bpf_probe_read(&data.comm, sizeof(data.comm), valp->comm);
	data.pid = pid;
	data.tpid = valp->tpid;
	data.ret = PT_REGS_RC(ctx);
	data.sig = valp->sig;

	events.perf_submit(ctx, &data, sizeof(data));
	infotmp.delete(&pid);

	return 0;
}
"""
