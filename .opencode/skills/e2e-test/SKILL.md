---
name: e2e-test
description: CTB 单题端到端测试设计、脚本实现与正确环境验证。读题后串行按子系统写用例并验证，再补子系统间交互。不负责取题和平台评测。
---

# CTB E2E Test

只按这个顺序做。一次只跑一个 subagent，禁止并发。

## 与 loop 的接口

loop 传入 `subject_root`、`profile`、`mode`、`round_target`、`work_order`（首轮为空）。返回 `delivery`。

只改 `python_framework/testaw.py`、`python_framework/udpunittest.py`，并写 `.ctb/design.json`（`ctb.design/v2`：`subsystems`、`hypotheses`、`tests`、`validation`、`delivery`；增量轮加 `increments`）。验证用 `.opencode/skills/e2e-test/scripts/e2e_evidence.py`。不写测试规格，不调用平台评测，不写 `session.json`。

## 流程

1. **读题。** 读 `subject_root` 里的题面和 `python_framework` 模板。
2. **识别子系统。** 运行 `python .opencode/skills/e2e-test/scripts/segment_subject.py <subject_root>`。结果写入 `design.subsystems`。只有一个模块时，下面仍做完第 3 步，跳过第 4 步。
3. **串行做每个子系统。** 按列表顺序，做完一个再启动下一个。每个子任务使用 `subagents/subsystem.md`，附上该段题面原文。该子任务在本子系统内设计、把尽量多的用例写进 `udpunittest.py`，并跑通验证。禁止同时启动第二个。
4. **交互用例。** 全部子系统验证通过之后，再补子系统之间的数据传递用例（上游写出的值被下游读到；传递失败时两边状态保持）。然后再验证一次。
5. **交付。** 把最后一次 `e2e_evidence.py run` 的结果写入 `validation`。通过则 `delivery.ready=true`，`answer_origin=self_authored`，`summary` 写子系统数、用例数、是否已补交互。把 `delivery` 交回 loop。
