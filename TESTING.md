# 工程规范与防退化（Regression）防线守则 (TESTING.md)

本项目为保证 Vibe Coding 过程中的系统稳定与需求准确对齐，杜绝“代码改来改去、修复了 A 破坏了 B”的现象，全体开发与 AI 协作必须严格遵守以下三条工程红线：

---

## 一、三大铁律（Engineering Gates）

### 1. 缺陷即测试（Defect-Driven Testing）
* **原则**：任何被确认的 Bug 或需求调整，**严禁直接修改业务代码**。
* **标准流程**：
  1. **先写失败测试**：在测试套件中编写针对该 Bug 或新规则的测试用例；
  2. **验证必报错**：确保该测试在现有代码下**必定红灯报错**；
  3. **修改业务代码**：调整实现逻辑，直至该测试变绿；
  4. **终身防退化**：**该测试用例永久保留**，纳入日常全量自动化回归跑道。

### 2. 契约防线与禁止静默容错（Contract & Fail-Fast）
* **原则**：拒绝“宽松容错导致的静默死锁或数据漂移”。
* **契约断言**：前后端字段、配置键名、函数返回结构必须通过测试强校验对齐。

### 3. 双层自动化门禁（CI Gates）
* **本地门禁（Pre-Commit Hook）**：位于 `.git/hooks/pre-commit`。每次在执行 `git commit` 前自动运行全量测试，测试未全绿则本地直接拒绝提交。
* **远端门禁（GitHub Actions CI）**：位于 `.github/workflows/ci.yml`。每次向主分支推送或提交 PR 时，在干净 runner 环境上自动执行全量测试，红灯严禁合入。

---

## 二、本地测试运行命令

```bash
# Python 项目示例
python -m unittest discover -s tests -p "test_*.py" -v
# 或
pytest tests/ -v

# Node.js 项目示例 (按项目实际情况替换)
# npm test
```
