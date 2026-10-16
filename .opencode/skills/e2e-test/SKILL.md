---
name: e2e-test
description: CTB 单题测试设计。铺场景，本地打正确版本记下返回，再按同一批场景写断言。不负责取题和平台评测。
---

# CTB E2E Test

loop 传入 `subject_root`、`profile`、`mode`、`round_target`、`work_order`。产物是 `python_framework/testaw.py`、`python_framework/udpunittest.py`、`.ctb/design.json`。返回 `delivery`。

自己读题，自己看本地接口怎么调、正确版本怎么跑、返回长什么样。下面只规定顺序。

1. 铺场景。把会让返回或状态不一样的情况铺开。
2. 在本地对正确版本跑这些场景，打印每一次返回，并原样记下来。
3. 这份记录就是 oracle。
4. 对同一批场景、同一调用顺序写断言，期望值只用记下的返回。断言写入上面的产物，`delivery` 写入 `.ctb/design.json`。

正确版本跑不起来就停下，在 `delivery` 里说明缺什么。不要编造返回值，也不要把有缺陷版本的返回写成金标准。
