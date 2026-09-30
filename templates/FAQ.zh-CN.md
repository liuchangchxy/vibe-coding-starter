# ❓ 常见问题与故障排查指南 (FAQ & Troubleshooting)

本文档整理了项目在安装、开发、部署与运行过程中最常见的疑问、典型报错及根因解决方案。

---

## 🛠️ 一、安装与环境排查 (Setup & Environment)

### Q1: 本地运行测试出现编码错误 (`UnicodeDecodeError: 'gbk' codec can't decode...`)？
* **根因**：在 Windows 系统上，默认终端编码可能是 GBK，若脚本中使用了裸 `subprocess.run(..., text=True)` 或未显式指定 UTF-8 读取文件，会导致解析包含中文的 UTF-8 文件时乱码崩溃。
* **解决办法**：
  1. Python 执行命令必须显式声明 `subprocess.run(..., text=True, encoding="utf-8", errors="replace")`；
  2. 读写文本文件统一声明 `open(..., encoding="utf-8")`；
  3. Windows PowerShell 可预先执行 `$OutputEncoding = [Console]::InputEncoding = [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()`。

### Q2: 提示缺少依赖或版本不兼容？
* **解决办法**：
  - Python: 建议使用虚拟环境 `python -m venv .venv` 并激活后执行 `pip install -r requirements.txt`。
  - Node.js: 建议使用 `pnpm install` 或 `npm ci` 锁定 `package-lock.json` 版本。
  - 终极方案：推荐在 VSCode 中直接使用 `.devcontainer/` 一键打开气密纯净容器。

---

## 🌐 二、全双语与暗黑模式 (i18n & Theme)

### Q3: 为什么切换到英文后，弹出的提示或者报错信息依然是中文？
* **根因**：后端 API 拼接了人类可读的自然语言（如 `raise HTTPException(detail="题目不存在")`），前端直接渲染了后端的硬编码字符串。
* **解决办法**：严格遵守全双语契约层法则，后端**严禁返回自然语言句子**，必须返回结构化枚举码与参数：`{"error_code": "TOPIC_NOT_FOUND", "params": {"id": 123}}`，由前端字典查表展示。

### Q4: 切换语言或主题时页面出现短暂的白屏或样式闪烁 (FOUC)？
* **根因**：主题或语言偏好在 JavaScript 框架完全加载（水合 Hydration）后才执行 DOM 类名变更。
* **解决办法**：在 HTML 入口 `<head>` 注入零依赖微内联脚本，优先从 `localStorage` 读取 `theme` / `locale` 并立即挂载到 `document.documentElement`，在绘制首屏前完成样式锁定。

---

## 📂 三、路径与可移植性 (Paths & Portability)

### Q5: 项目在他人电脑或 CI 虚拟机中运行时报错 `FileNotFoundError: C:\Users\...`？
* **根因**：违反了【严禁硬编码绝对路径】底线，在源码中写死了本机的物理绝对路径。
* **解决办法**：
  - Python 中统一使用：`Path(__file__).resolve().parent` 计算相对项目基准目录；
  - Node.js 中统一使用：`import.meta.url` 或 `path.resolve(__dirname, ...)`；
  - 外部路径、持久化数据路径统一通过 `.env` 环境变量注入，并提供安全默认相对路径。

---

## 🧪 四、测试与自动化门禁 (Testing & Gates)

### Q6: 为什么本地 `git commit` 会被拒绝？
* **根因**：项目激活了 `.git/hooks/pre-commit` 门禁。当本地存在未通过的单元测试、或者检出了未被 i18n 化的硬编码文本/被篡改的断言时，门禁将物理拦截提交。
* **解决办法**：
  1. 运行本地测试（如 `python -m unittest discover tests` 或 `npm test`）查看具体红灯用例；
  2. 正面修复业务代码直至全绿，严禁使用 `git commit --no-verify` 绕过检查。

### Q7: 测试报告显示 `skipped > 0`，是否可以通过交付验收？
* **根因**：根据 standards/TESTING.md 门禁，`skipped` 不代表通过。必须明确区分是由于缺少外部硬件造成的“环境性跳过”，还是目标测试用例未真正运行的“断言跳过”。
* **解决办法**：断言性跳过一票否决，必须真实执行；环境性跳过必须在文档中逐条声明豁免原因。
