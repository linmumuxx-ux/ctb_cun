---
name: e2e-test
description: CTB 单题测试设计。探索式状态空间随机游走：建地图，随机游走记录判定，再据此生成用例和断言。不负责取题和平台评测。
---

# CTB E2E Test

loop 传入 `subject_root`、`profile`、`mode`、`round_target`、`work_order`。产物是 `python_framework/testaw.py`、`python_framework/udpunittest.py`。返回 `delivery`。不写 `.ctb/design.json`，loop 也不要把它当本技能的必交产物。

自己读题，自己看本地接口怎么调。这是探索式的状态空间随机游走，下面只规定顺序。

1. 构建状态和地图。
2. 随机游走遍历，过程中记录操作序列。
3. 每个状态都查询并记录判定。
4. 据此生成用例和断言脚本，写入上面的产物。用例和断言只用第 3 步记下的判定。
