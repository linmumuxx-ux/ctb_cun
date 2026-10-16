# 子系统子任务

你只处理编排器指定的一个子系统。不要启动别的子任务，不要写其他子系统，不要写子系统之间的交互用例。

读编排器给的题面摘录和现有 `python_framework/testaw.py`、`udpunittest.py`。在本子系统内设计并写入尽量多的测试用例，覆盖题面里这个子系统的规则、边界和失败路径。用例互相独立，从初始状态开始。

写完后运行：

```text
python .opencode/skills/e2e-test/scripts/e2e_evidence.py run --framework <python_framework> --out-dir <subject_root>/.ctb/evidence/<子系统id>
```

正确环境必须通过。失败就改用例再跑，直到通过。把本子系统的假设和用例 id 补进 `.ctb/design.json` 的 `hypotheses` 和 `tests`。不要另写测试规格。
