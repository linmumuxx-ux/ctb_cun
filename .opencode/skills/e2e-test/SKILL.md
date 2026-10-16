---
name: e2e-test
description: CTB 单题端到端测试设计、脚本实现、正确环境验证及增量修复；不负责取题和平台评测。编排器先识别子系统，再按子系统设计判别用例，产出可验证的 testaw.py / udpunittest.py 与 .ctb/design.json。
---

# CTB E2E Test

编排器。隐藏错误只有在用例走到错误逻辑（可达）、输入让错误实现表现不同（激发）、差异被断言观察到（传播）时才会被判出。判别方法以 `references/design-playbook.md` 为准（下文用 §n 指代），框架与验证以 `references/ilearning-framework.md` 为准。子系统 subagent 使用 `subagents/subsystem.md`，不另写测试规格说明书或 testspec。

## 输入、输出与边界

**输入**（由 loop 提供，名称保持不变）：`subject_root`、`profile`（FAST/BALANCED/THOROUGH/auto）、`mode`、`round_target`（下一次评测的轮号）、`work_order`（首轮为空；增量轮是 loop 用台账生成的本题反馈摘要）。

**输出**（路径与写入者不变）：

- `python_framework/testaw.py`、`python_framework/udpunittest.py`：唯二的正式交付文件，只有编排器写入；
- `.ctb/design.json`：本 Skill 是唯一写入者；
- `.ctb/evidence/<标签>/`：`e2e_evidence.py` 的验证日志、`validation.json`、轨迹；
- `.ctb/tmp/`：探测与诊断，不属于交付。

**禁止**：

- 调用 `subject_api.get()` / `evaluation()`；写 `session.json`；修改 `testtool.py`、`timeout.py`、`tp000.jar`、规格；
- 用隐藏答案、其他题的具体答案、BUG ID 或分类去猜缺陷内容；
- 通过删断言、放宽匹配、吞异常、伪造日志让测试通过；
- 自建 socket/UDP 客户端；让 testcase 依赖其他 testcase 的执行顺序；
- 把子系统摘录或用例草稿写成测试规格说明书、testspec 或其他中间规格文档。

## 切分

读 `subject_root` 下的题面 Markdown（跳过 `.ctb/`、`python_framework/`）。切分算法以 `.opencode/skills/e2e-test/scripts/segment_subject.py` 为准，编排器调用它，不另写一套规则：

- 统计全部 `##` 标题，去掉通用标题（命令、规则、概述、说明、错误码等，见脚本中的 `GENERIC`）；
- 有效二级标题不少于 2 个时，每个标题是一个子系统；
- 否则整题是一个模块，`single` 为 true，在当前 Agent 中按 `subagents/subsystem.md` 设计，不启动 subagent。

接口、类、状态和数据流用于给子系统摘录划界、给联动用例找箭头，不单独再切一刀。题面没有写成章节时，不要把一张命令表拆成多个子系统。

## 工作流

重复接手同一题时先读已有 `design.json`，只做变化的部分。子任务返回的 JSON 由编排器合并进 `design.json`，不落成另一份文档。

### S1 契约卡（手册 §2，框架文档 §1）

读规格、模板、AW、testtool。整理命令表、观察通道、复位、限制、`oracle_policy`、歧义。产出 `contract`、`spec_sha256`。每个命令要有响应列表和出处。入口或命令格式无法从公开资料确认且挡住用例时，只做一次框架文档 §8 的最小探测；仍不清楚则记 GAP，返回 `blocked`。

### S2 切分并设计

1. 运行 `segment_subject.py <subject_root>`，把结果写入 `design.subsystems`。单模块的 `agent` 为 `current`，多模块为 `subagent`。
2. 单模块：当前 Agent 按 `subagents/subsystem.md` 完成本模块的机制、假设和 `case_sketches`。
3. 多模块：同一轮并行启动一个 subagent 对应一个子系统。每个子任务的提示词是模板全文，加上该段题面原文、`contract` 短列表、`profile`，以及 `work_order` 里与该子系统用例相关的部分。子任务之间互不可见，都不写正式文件。
4. 合并：假设编号加上子系统前缀；`reach`、`infect`、`propagate` 都相同的只留一条；机制写入 `mechanisms[]` 并带上 `subsystem`。子任务的 `gaps` 并入 `design.gaps`。
5. 联动：仅当子系统不少于两个，且题面写出了模块之间的数据传递。对每一条传递补三类假设，记入 `design.linkages`，并各有一条 `case_sketches`：传递成功且下游读到的值等于上游写出的值；上游比下游门槛少 1 时下游拒绝，两边状态保持；同一结果重复提交只生效一次。题面没有这条传递就不编。
6. 此时还不写脚本。先按手册 §3 做交叉核对 (a)–(d)，规定技术写入 `required_techniques`。

### S3 故障假设收口（手册 §4 §5，规定技术 §7，质量 §8）

合并后的 `hypotheses[]` 必须能对上算子。广度按 Profile：先让每个机制的核心效果和每个守卫都有 P0，再按 profile 加交互类算子，最后补规定技术的剩余单元。`check-design` 里没有假设指向的机制元素，要么补假设，要么写下理由。

### S4 实现（手册 §6，框架文档 §3–§5）

编排器把草稿收成 `udpunittest.py` 的用例：构造时每步断言，激发，按观察阶梯断言，必要时做后续操作。在 `testaw.py` 接入默认关闭的轨迹钩子（框架文档 §4）。每条用例登记到 `tests{}`。先实现各机制的 P0 并跑通 S5，再补其余。`lint` 不得留下未说明的 `unobserved_aw_call`。

### S5 真实验证（框架文档 §6）

`python .opencode/skills/e2e-test/scripts/e2e_evidence.py run --framework <fw> --out-dir <root>/.ctb/evidence/<标签> --trace`。把 `validation.json` 的 `status`、`files_sha256`、`collected_count`、`run_count`、`testcase_ids`、`id_match`、`summary`、`log_paths`、`command` 写入 `design.validation`。`status=passed` 且没有 blocker 才继续。同一失败两次都没有新证据则返回 `blocked`。正确环境通过只说明脚本与正确实现兼容。

### S6 判别审计（手册 §9）

`trace-report`（`--expected-codes` 填规格中的全部响应码）、`lint`、`check-design`。审计改了脚本就回到 S5 完整重跑。产出 `audit` 和 `gaps`。

### S7 交付

写入 `delivery`：`ready`、`blockers`、`answer_origin`（只用公开规格、本题正确 JAR 和本手册时为 `self_authored`）、`summary`（不超过 10 行：子系统数、是否单模块、联动条数、假设数及 P0、收集/执行数、规定技术、主要 GAP）。

`ready=true` 需要：S5 通过且摘要与当前文件一致，P0 假设全部 `verified` 或有理由的 `gap`，S6 的 A–F 无未处理项。否则 `ready=false` 并列出 blockers。

返回给 loop 的仍是 `delivery` 和 `validation.status`，不复述设计细节。

## 增量模式

`work_order` 含上一轮冻结快照、每条用例的 NEW/REPEAT/MISS/UNKNOWN、命中的不透明 BUG 令牌、分类汇总和 loop 观察到的事实。

1. 按手册 §10 做命中热图和 R/I/P 分诊。优先级：模型缺口，未命中机制的修复，已命中机制的交互类算子；
2. 已有用例默认保留。要删除或改变曾经命中的用例时写入 `increments[].removed_tests`；
3. 多子系统时，只把相关用例的分类分给对应 subagent；联动缺口由编排器补；
4. 写 `increments[]`：`for_round`、`input_focus`、`new_hypotheses`、`repaired_tests`、`model_corrections`、`removed_tests`、`why_old_insufficient`；
5. 重新执行 S5–S7。没有合格增量时 `delivery.ready=false`，`blockers` 含 `no_new_hypothesis`。

## Profile

profile 只调整每个子系统内部的广度和深度，不决定是否拆 subagent，也不降低规定技术、断言和框架要求。

| profile | 假设范围 |
| --- | --- |
| FAST | 所有机制的 P0 假设 + 规定技术的单元 |
| BALANCED | FAST + 存在相应结构的交互类算子（`G-SCOPE` / `E-SCOPE` / `E-ACCUM` / `L-STALE` / `S-TRANS` / `R-LEAK`） |
| THOROUGH | BALANCED + 跨机制业务轨迹、规格定义了优先级时的 `G-ORDER`、`T-TIME` 细粒度、手册 §11 的覆盖诊断 |
| auto | 机制不超过 3 且无状态机、时间或多对象 → FAST；否则 BALANCED；规格同时包含多实体、状态机、时间推进中的至少两类 → THOROUGH。结论写入 `profile` |

## design.json

在原有 `ctb.design/v2` 上增加 `subsystems` 与 `linkages`。其余字段、`hypotheses` 和 `tests` 的形状不变，loop 的 `gate` 仍只读 `delivery`、`validation`、`hypotheses`、`increments`。

```json
{
  "schema": "ctb.design/v2",
  "subject_id": "题号字符串",
  "spec_sha256": null,
  "profile": "BALANCED",
  "subsystems": [{"id": "S01", "name": "题面标题或章节名", "single": true, "agent": "current"}],
  "linkages": [{"id": "L01", "from": "S01", "to": "S02", "kind": "pass|short_by_one|idempotent", "hypotheses": ["H-L01"]}],
  "oracle_policy": {"precedence": "spec_default", "source": null},
  "contract": {"framework": {}, "commands": [], "observers": [], "reset": null, "limits": {}, "ambiguities": []},
  "mechanisms": [],
  "required_techniques": [],
  "quality_applicability": {},
  "hypotheses": [],
  "tests": {},
  "reference_analysis": {"status": "not_run", "read": [], "findings": [], "uncertain": []},
  "audit": {},
  "gaps": [],
  "validation": {"status": "not_run"},
  "increments": [],
  "delivery": {"ready": false, "blockers": [], "answer_origin": "unconfirmed", "summary": null}
}
```

未知填 `null`，不填 0。没有真实运行就保持 `validation.status` 为 `not_run`。`verified` 只用于当前验证版本里真实收集到的用例。
