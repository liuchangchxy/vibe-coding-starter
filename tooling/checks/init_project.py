#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
init_project.py - 新开源项目标准化脚手架初始化器
基于 Vibe Coding Starter 初始化任何新开源项目时，自动注入标准交付物：
1. 自动部署根目录 SPONSOR.md (赞助渠道与鸣谢墙)
2. 自动部署根目录 FAQ.md (常见排查与故障处理指南)
3. 自动安装防测试篡改与硬编码路径扫描的 Pre-Commit 本地门禁
4. 自动初始化多语言字典骨架 (locales/zh-CN.json, locales/en-US.json)
"""

import sys
import shutil
from pathlib import Path

# 针对 Windows 终端 GBK 编码进行加固
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

def init_project(project_name: str = "MyOpenSourceApp"):
    root = Path(__file__).resolve().parent.parent.parent
    templates_dir = root / "templates"

    print("============================================================")
    print(f" 🚀 [Vibe Coding Starter] 初始化新开源项目: {project_name}")
    print("============================================================")

    # 1. 部署 SPONSOR.md
    target_sponsor = root / "SPONSOR.md"
    src_sponsor = templates_dir / "SPONSOR.md"
    if src_sponsor.exists() and not target_sponsor.exists():
        content = src_sponsor.read_text(encoding="utf-8")
        content = content.replace("<your-project>", project_name.lower())
        target_sponsor.write_text(content, encoding="utf-8")
        print("✅ [标准交付物] 已部署根目录 SPONSOR.md (赞助渠道与鸣谢墙)")
    else:
        print("ℹ️ [标准交付物] 根目录 SPONSOR.md 已存在或源模板缺失，跳过。")

    # 2. 部署 FAQ.md
    target_faq = root / "FAQ.md"
    src_faq = templates_dir / "FAQ.md"
    if src_faq.exists() and not target_faq.exists():
        content = src_faq.read_text(encoding="utf-8")
        target_faq.write_text(content, encoding="utf-8")
        print("✅ [标准交付物] 已部署根目录 FAQ.md (常见问题排查与技术问答)")
    else:
        print("ℹ️ [标准交付物] 根目录 FAQ.md 已存在或源模板缺失，跳过。")

    # 3. 初始化多语言字典骨架
    locales_dir = root / "locales"
    if not locales_dir.exists():
        locales_dir.mkdir(parents=True, exist_ok=True)
        zh_json = locales_dir / "zh-CN.json"
        en_json = locales_dir / "en-US.json"
        if not zh_json.exists():
            zh_json.write_text('{\n  "app": {\n    "name": "' + project_name + '",\n    "welcome": "欢迎使用"\n  }\n}\n', encoding="utf-8")
        if not en_json.exists():
            en_json.write_text('{\n  "app": {\n    "name": "' + project_name + '",\n    "welcome": "Welcome"\n  }\n}\n', encoding="utf-8")
        print("✅ [全双语基准] 已创建初始多语言字典骨架 (locales/zh-CN.json, locales/en-US.json)")

    # 4. 执行 setup-hooks.py 激活门禁
    setup_hooks_script = root / "tooling" / "checks" / "setup-hooks.py"
    if setup_hooks_script.exists():
        import subprocess
        subprocess.run([sys.executable, str(setup_hooks_script)], check=False)

    print("\n🎉 项目基础工程设施已全部就绪！")
    print("👉 请在 SPEC.md 中细化系统业务契约，开启真正的 Spec-Driven 开发！")
    print("============================================================\n")

if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "MyOpenSourceProject"
    init_project(name)
