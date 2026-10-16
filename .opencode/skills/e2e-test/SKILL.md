---
name: e2e-test
description: CTB 单题测试设计。串行按子系统设计、写用例、验证，再补交互。不负责取题和平台评测。
---

# CTB E2E Test

loop 传入 `subject_root`、`profile`、`mode`、`round_target`、`work_order`。产物是 `python_framework/testaw.py`、`python_framework/udpunittest.py`、`.ctb/design.json`。返回 `delivery`。

自己读题，自己理解规则，自己决定用例怎么写、怎么验证。

按子系统串行做，一次只启动一个 subagent，禁止并发。提示词用 `subagents/subsystem.md`。每个子系统：设计 → 写尽量多的用例 → 验证。全部子系统做完后，再写子系统之间的交互用例。
