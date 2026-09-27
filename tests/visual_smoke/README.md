# 视觉冒烟（Web 项目按需启用）

## 做什么

无头浏览器逐路由截图 × 双视口（桌面 1280 + 手机 390），截图归档备查，不入库。

## 两层判据

1. **机器判白屏**：截图唯一颜色数 <= 1，或有效像素占比过低 → 红灯（可在 CI 跑）。
2. **人眼/AI 并排评审**：把截图并排放（参考实现、竞品、上一版），评"好不好看"——这层机器测不了，见 TESTING.md 测试层级第 6 条。

## 用法

```bash
# 1. 起应用（任意静态服务或 dev server）
# 2. 起无头 Chrome（桌面视口）
"Google Chrome" --headless=new --no-sandbox --window-size=1280,900 \
  --remote-debugging-port=9222 --user-data-dir=/tmp/shotprof about:blank &
# 3. 截图（hash 路由示例；非 hash 路由把 `#` 去掉即可）
node shot.mjs http://localhost:9222 http://localhost:8000 ./shots / /settings /trash
# 4. 手机视口再来一遍（换端口 + 换窗口大小 + 换输出目录）
```

## 约定

- 路由 `#` 前缀只适用于 hash 路由的 SPA；按项目路由方式调整 `Page.navigate` 的 URL 拼接。
- `document.readyState` 只是"载入完"，首帧稳定靠 `--settle`（默认 2500ms）；重型首屏按需调大。
- 截图产物只做评审归档，不提交进仓库（体积大、diff 无意义）。
