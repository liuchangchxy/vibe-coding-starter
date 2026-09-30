# 规则总账 (RULES.md)

> **这是什么**：一条规则一行、一个稳定 ID、**并且只有一个归属文件**。其它任何需要这条规则的地方一律引用，不复述。
>
> **为什么要它**：同一条规则写在三处就会漂移成三条不同的规则。本总账是防漂移契约，也是任何重组的**安全网**——`tooling/checks/check_docs.py` 会在某条规则的归属文件不再包含它时让 CI 变红。**你不可能悄悄弄丢一条规则而不被发现。**

<p align="center"><a href="RULES.zh-CN.md">简体中文</a> · <a href="RULES.md">English</a></p>

---

## 1. 单一真理源归属表

改任何规则前先读这张表。规则在这里，就**只在这里改**。

| 规则域 | 唯一归属 | 其它位置 |
|---|---|---|
| AI 行为、三大引擎、避坑清单 | `AGENTS.md` | 只引用 |
| 严重度 P0–P3 | `standards/TESTING.md` §三 | `AGENTS.md`、`standards/EXECUTION.md` 引用 |
| 收敛交付标准 (DoD) | `standards/TESTING.md` §三 | 只引用 |
| 测试门禁、层级、证据 | `standards/TESTING.md` §一/§二 | 只引用 |
| 审查攻击配方 | `standards/REVIEWING.md` | 只引用 |
| 执行工序、Rulings | `standards/EXECUTION.md` | 只引用 |
| 架构推导法 | `standards/ARCHITECTURE.md` | 只引用 |
| 本地化与主题 | `standards/LOCALIZATION.md` | `SPEC.md` §7 摘要 + 引用 |
| 产品业务规则 | `SPEC.md` | 只引用 |
| 决策与原因 | `docs/DECISIONS.md` | 只引用 |
| 需求 ↔ 证据状态 | `docs/REQUIREMENTS_TRACEABILITY.md` | 只引用 |

**不变量**：`SPEC.md` 说*做什么*，`standards/` 说*怎么做工程*，`docs/` 记*发生过什么*。一条规则只出现在这三者中的一个。

---

## 2. 通用规则清单

**执行方式**列：脚本名 = 有物理门禁；`纪律` = 流程规则，暂无自动化检查。

### A — AI 行为准则（`AGENTS.md`）

| ID | 规则 | 归属 | 执行方式 |
|---|---|---|---|
| A-01 | SPEC 是任何业务改动的唯一真理源 | `AGENTS.md` | 纪律 |
| A-02 | 非破坏性操作；未经明确许可不得删除或覆盖 | `AGENTS.md` | 纪律 |
| A-03 | 防测试篡改；严禁伪造全绿 | `AGENTS.md` | `guard_test_tampering.py` |
| A-04 | 禁止硬编码绝对路径 | `AGENTS.md` | `scan_hardcoded_paths.py` |
| A-05 | 本地化与主题是一等公民 | `AGENTS.md` | `check_docs.py` |
| A-06 | 开源标配交付物（SPONSOR、FAQ） | `AGENTS.md` | `test_smoke.py` |
| A-07 | 交付必须全绿 | `AGENTS.md` | 纪律 |
| A-08 | 强制端到端验证；严禁把 `skipped` 当通过 | `AGENTS.md` | 纪律 |
| A-09 | 口头意图先自动落 SPEC，再动代码 | `AGENTS.md` | 纪律 |
| A-10 | 新项目强制基线注入 | `AGENTS.md` | `init_project.py` |
| A-11 | 歧义反问拦截：含糊需求先给 2–3 个选项 | `AGENTS.md` | 纪律 |
| A-12 | 高风险改动前打微快照 | `AGENTS.md` | `checkpoint.py` |
| A-13 | 决策留痕写入 docs/DECISIONS.md | `AGENTS.md` | 纪律 |
| A-14 | 1 变 4 根因发散协议 | `AGENTS.md` | 纪律 |
| A-15 | 严重度台阶 P0–P3 | `AGENTS.md` | 纪律 |
| A-16 | 收敛 DoD + 裁定清单；禁止静默裁定 | `AGENTS.md` | 纪律 |
| A-17 | 自我进化避坑清单 | `AGENTS.md` | 纪律 |
| A-18 | 复杂度开关：小任务禁用重流程 | `AGENTS.md` | 纪律 |
| A-19 | SPEC 里有 ≠ 已实现；证据单独记录 | `AGENTS.md` | 纪律 |
| A-20 | 测试层级不得互相冒充 | `AGENTS.md` | 纪律 |
| A-21 | UI 类模糊评价走五维清单，产出改/不改选择题 | `AGENTS.md` | 纪律 |
| A-22 | 冻结需求的备选调研属探索，结论不写入 SPEC | `AGENTS.md` | 纪律 |

### A-L — 避坑清单（`AGENTS.md` 末尾 25 条）

| ID | 教训 | 归属 | 执行方式 |
|---|---|---|---|
| A-L01 | 严禁只改代码不同步需求 | `AGENTS.md` | 纪律 |
| A-L02 | 交付前测试必须全绿 | `AGENTS.md` | 纪律 |
| A-L03 | 严禁 `--no-verify` | `AGENTS.md` | `setup-hooks.py` |
| A-L04 | 严禁只跑 Mock 测试 | `AGENTS.md` | 纪律 |
| A-L05 | 严禁把 `skipped` 当通过 | `AGENTS.md` | 纪律 |
| A-L06 | `subprocess.run(text=True)` 必须声明 UTF-8 | `AGENTS.md` | 纪律 |
| A-L07 | 严禁篡改旧测试预期值伪造全绿 | `AGENTS.md` | `guard_test_tampering.py` |
| A-L08 | 修 Bug 严禁孤立改单行 | `AGENTS.md` | 纪律 |
| A-L09 | 务实调研，不看 Star 数论事 | `AGENTS.md` | 纪律 |
| A-L10 | OSS 评估必须聚焦目标项目 | `AGENTS.md` | 纪律 |
| A-L11 | 严禁死扣局部细节压过全局目标 | `AGENTS.md` | 纪律 |
| A-L12 | 防真理源 (SPEC) 早产与污染 | `AGENTS.md` | 纪律 |
| A-L13 | 证据状态分离 | `AGENTS.md` | 纪律 |
| A-L14 | 真实链路分层，不得互相冒充 | `AGENTS.md` | 纪律 |
| A-L15 | 复杂度止损 | `AGENTS.md` | 纪律 |
| A-L16 | SPA 入口必须零缓存 | `AGENTS.md` | 纪律 |
| A-L17 | 分步向导非阻塞流转 | `AGENTS.md` | 纪律 |
| A-L18 | 受限视口物理预算（顶栏 ≤ 44px） | `AGENTS.md` | 纪律 |
| A-L19 | 凭证零入库 | `AGENTS.md` | `test_secret_hygiene.py` |
| A-L20 | 推送前脱敏 census | `AGENTS.md` | `test_secret_hygiene.py` |
| A-L21 | 历史即公开面；泄露须改写历史 | `AGENTS.md` | 纪律 |
| A-L22 | 每个 Bug 触发 1 变 4 协议 | `AGENTS.md` | 纪律 |
| A-L23 | 绝对路径零容忍 | `AGENTS.md` | `scan_hardcoded_paths.py` |
| A-L24 | 通用多语言门禁 | `AGENTS.md` | `check_docs.py` |
| A-L25 | 开源标准交付物 | `AGENTS.md` | `test_smoke.py` |

### T — 测试门禁（`standards/TESTING.md`）

| ID | 规则 | 归属 | 执行方式 |
|---|---|---|---|
| T-01 | 缺陷即测试：先写失败测试再改实现 | `standards/TESTING.md` | 纪律 |
| T-02 | 防测试篡改物理门禁 | `standards/TESTING.md` | `guard_test_tampering.py` |
| T-03 | 禁止硬编码绝对路径门禁 | `standards/TESTING.md` | `scan_hardcoded_paths.py` |
| T-04 | 契约防线与禁止静默容错 | `standards/TESTING.md` | 纪律 |
| T-05 | 1 变 4 发散；动手前先 census | `standards/TESTING.md` | 纪律 |
| T-06 | 规范即测试：源码自扫描守卫三件套 | `standards/TESTING.md` | `check_docs.py` |
| T-07 | 门禁即证据：新门禁自带红色实证 | `standards/TESTING.md` | 纪律 |
| T-08 | 测试层级与证据报告 | `standards/TESTING.md` | `TEST_EVIDENCE_TEMPLATE.md` |
| T-09 | 凭证卫生门禁 | `standards/TESTING.md` | `test_secret_hygiene.py` |
| T-10 | 双层物理门禁；发布门与 CI 门同构 | `standards/TESTING.md` | `ci.yml` |
| T-11 | 字典键对齐与无硬编码文案门禁（按需） | `standards/TESTING.md` | `check_docs.py` |
| T-12 | 界面主题与端侧预算门禁（按需） | `standards/TESTING.md` | 纪律 |
| T-13 | 异步与偶发失败排查（按需） | `standards/TESTING.md` | 纪律 |
| T-14 | 收敛交付标准：P0/P1 清零 + 测试 100% + `skipped=0` | `standards/TESTING.md` | 纪律 |

### R — 审查配方（`standards/REVIEWING.md`）

| ID | 规则 | 归属 | 执行方式 |
|---|---|---|---|
| R-01 | 双裁决：规格符合 + 质量分级 | `standards/REVIEWING.md` | 纪律 |
| R-02 | 空转测试识别（删掉实现还绿吗） | `standards/REVIEWING.md` | 纪律 |
| R-03 | 边界与量化数学 | `standards/REVIEWING.md` | 纪律 |
| R-04 | 证据链倒挂检测（"不可能失败的门禁"） | `standards/REVIEWING.md` | 纪律 |
| R-05 | 自证向量陷阱 | `standards/REVIEWING.md` | 纪律 |
| R-06 | 跨端键一致性 | `standards/REVIEWING.md` | 纪律 |
| R-07 | 缓存死水与交付穿透（物理指纹） | `standards/REVIEWING.md` | 纪律 |
| R-08 | 审查者三律（亲手跑门禁、红要能复现、对抗姿态） | `standards/REVIEWING.md` | 纪律 |

### E — 执行工序（`standards/EXECUTION.md`）

| ID | 规则 | 归属 | 执行方式 |
|---|---|---|---|
| E-01 | 适用开关：规模旋钮、宿主适配、严重度统一 | `standards/EXECUTION.md` | 纪律 |
| E-02 | 全流程八步与各自的文件产物 | `standards/EXECUTION.md` | 纪律 |
| E-03 | Carry-forward：审查发现不得蒸发 | `standards/EXECUTION.md` | 纪律 |
| E-04 | 阶段收尾必须披露裁定清单 | `standards/EXECUTION.md` | 纪律 |
| E-05 | 进度账本 × 微快照（双轨不可互替） | `standards/EXECUTION.md` | `checkpoint.py` |
| E-06 | 事故条目：症状 → 根因链 → 最小修复 → 验证 → 防复发 | `standards/EXECUTION.md` | 纪律 |
| E-07 | 反模式清单 | `standards/EXECUTION.md` | 纪律 |
| E-08 | 严禁把单次实测数字写成文档事实 | `standards/EXECUTION.md` | 纪律 |

### C — 架构方法（`standards/ARCHITECTURE.md`）

| ID | 规则 | 归属 | 执行方式 |
|---|---|---|---|
| C-01 | 七步推导，严格按序 | `standards/ARCHITECTURE.md` | 纪律 |
| C-02 | 三判据：改得便宜 / 用得难错 / 坏了能看见 | `standards/ARCHITECTURE.md` | 纪律 |
| C-03 | 抄/造判据：商品层 / 规范层 / 差异层 | `standards/ARCHITECTURE.md` | 纪律 |

### L — 本地化与主题（`standards/LOCALIZATION.md`）

| ID | 规则 | 归属 | 执行方式 |
|---|---|---|---|
| L-01 | 零硬编码自然语言 | `standards/LOCALIZATION.md` | `check_docs.py` |
| L-02 | 服务端严禁拼接人类句子 | `standards/LOCALIZATION.md` | 纪律 |
| L-03 | 字典键双向对齐门禁 | `standards/LOCALIZATION.md` | `check_docs.py` |
| L-04 | 纯裸数据传递（ISO-8601 UTC、纯数值） | `standards/LOCALIZATION.md` | 纪律 |
| L-05 | 语言状态单一真理源，切换必须扇出 | `standards/LOCALIZATION.md` | 纪律 |
| L-06 | 排版弹性预算 30%–50% | `standards/LOCALIZATION.md` | 纪律 |
| L-07 | 缺 key 降级策略（显示 key + 开发环境警告） | `standards/LOCALIZATION.md` | 纪律 |
| L-08 | 统一 `Accept-Language` 标头 | `standards/LOCALIZATION.md` | 纪律 |
| L-09 | 结构化错误码，严禁句子 | `standards/LOCALIZATION.md` | 纪律 |
| L-10 | 持久化枚举必须是中性 code | `standards/LOCALIZATION.md` | 纪律 |
| L-11 | 内容多语言降级链 `target → default → raw` | `standards/LOCALIZATION.md` | 纪律 |
| L-12 | AI 提示词透传 locale + "Respond strictly in {target_language}" | `standards/LOCALIZATION.md` | 纪律 |
| L-13 | 主题单一真理源（`light`/`dark`/`system`） | `standards/LOCALIZATION.md` | 纪律 |
| L-14 | 语义化 Design Token，禁裸色值 | `standards/LOCALIZATION.md` | 纪律 |
| L-15 | 零闪烁 (Zero FOUC) | `standards/LOCALIZATION.md` | 纪律 |
| L-16 | 分端适配器必须分端应用，不得全局套用 | `standards/LOCALIZATION.md` | 纪律 |

---

## 3. 维护本总账

1. **新增规则**：先在归属文件里写好，再到这里加一行（取下一个空号），并注明谁来执行它。
2. **修改规则**：改归属文件。**绝不在第二个文件里复述这条规则**——只放链接。
3. **删除规则**：行与规则在同一次提交里一起删，并在 `docs/DECISIONS.md` 记录原因。
4. **门禁**：`python tooling/checks/check_docs.py` 校验每个 ID 的归属文件仍然存在且仍含该规则。每次提交前跑。
