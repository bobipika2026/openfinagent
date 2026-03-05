# 🎬 TradeFlow AI 演示 GIF 录制需求

> 用于 README.md 和其他宣传材料的动图演示

---

## 📋 录制清单

### 1. 核心功能演示（README 主图）

**时长：** 15-20 秒  
**分辨率：** 1280x720 或 1920x1080  
**帧率：** 30fps

**脚本：**

```
[0-2 秒] 
屏幕显示 TradeFlow AI 欢迎界面
字幕："用说话的方式做量化交易"

[2-5 秒]
光标移动到代码编辑器
输入：Strategy.from_natural_language(
显示文字："当 5 日均线上穿 20 日均线时买入，下穿时卖出"

[5-8 秒]
点击"生成策略"按钮
显示加载动画（2 秒）
✅ 策略已生成

[8-12 秒]
自动展示生成的 Python 代码
代码高亮显示
镜头缓慢推进

[12-15 秒]
点击"回测"按钮
显示回测进度条
✅ 回测完成

[15-18 秒]
展示回测结果卡片：
- 年化收益：23.5%
- 最大回撤：12.3%
- 夏普比率：1.85

[18-20 秒]
TradeFlow AI Logo + GitHub 链接
字幕："立即开始 → github.com/tradeflow-ai"
```

**工具推荐：**
- macOS: ScreenFlow / QuickTime + GIPHY Capture
- Windows: Camtasia / OBS Studio
- Linux: OBS Studio + ffmpeg

**后期处理：**
```bash
# 使用 ffmpeg 转换为 GIF
ffmpeg -i input.mp4 -vf "fps=30,scale=1280:-1:flags=lanczos" output.gif

# 优化 GIF 大小
gifsicle -O3 --colors 256 output.gif -o output_optimized.gif
```

---

### 2. 快速上手演示（教程用）

**时长：** 30 秒  
**分辨率：** 1920x1080

**脚本：**

```
[0-3 秒]
终端输入：pip install tradeflow-ai
进度条快速完成

[3-8 秒]
打开 Python
输入导入语句：from tradeflow import Strategy

[8-15 秒]
创建策略：
strategy = Strategy.from_natural_language(
    "当 5 日均线上穿 20 日均线时买入，下穿时卖出，止损 5%"
)

[15-20 秒]
执行回测：
results = strategy.backtest("2023-01-01", "2024-01-01")

[20-25 秒]
查看结果：
print(results.summary())
展示格式化输出

[25-30 秒]
绘制资金曲线：
results.plot_equity_curve()
图表逐渐绘制完成
```

---

### 3. 多 Agent 协作演示

**时长：** 25 秒

**脚本：**

```
[0-5 秒]
展示三个 Agent 图标：
📚 Research Agent
💼 Trading Agent  
🛡️ Risk Agent

[5-10 秒]
Research Agent 分析市场
显示分析结果：
"新能源板块：看涨，置信度 78%"

[10-15 秒]
Trading Agent 执行交易
显示订单：
买入：宁德时代 100 股
买入：比亚迪 50 股

[15-20 秒]
Risk Agent 监控
显示风险指标：
仓位：45% ✓
回撤：3.2% ✓
VaR: 2.1% ✓

[20-25 秒]
三个 Agent 协同工作动画
字幕："AI 投顾团队，24 小时守护"
```

---

### 4. 策略市场演示

**时长：** 20 秒

**脚本：**

```
[0-5 秒]
打开策略市场页面
展示热门策略排行榜

[5-10 秒]
点击"双均线策略 v2.3"
显示策略详情：
- 年化收益：28.5%
- 使用人数：1,234
- 评分：⭐⭐⭐⭐⭐

[10-15 秒]
点击"一键导入"
策略添加到我的策略库

[15-20 秒]
修改参数并回测
显示优化后的结果
```

---

## 🎨 视觉规范

### 配色方案
```
主色调：
- 科技蓝：#2563EB
- 成功绿：#10B981
- 警告橙：#F59E0B
- 危险红：#EF4444

背景：
- 浅色模式：#FFFFFF / #F3F4F6
- 深色模式：#1F2937 / #111827

代码高亮：
- 关键字：#7C3AED
- 字符串：#059669
- 注释：#6B7280
- 函数：#2563EB
```

### 字体
```
代码字体：JetBrains Mono / Fira Code
标题字体：Inter / SF Pro Display
正文字体：系统默认
```

### 动画风格
- 转场：平滑淡入淡出
- 强调：轻微缩放 + 阴影
- 加载：旋转进度条
- 成功：勾选动画 + 绿色

---

## 📸 截图清单

### 静态截图（用于文档和官网）

1. **首页 Hero**
   - 分辨率：1920x1080
   - 内容：欢迎界面 + 核心功能展示

2. **策略编辑器**
   - 分辨率：1920x1080
   - 内容：代码编辑器 + 自然语言输入框

3. **回测结果页**
   - 分辨率：1920x1080
   - 内容：资金曲线 + 统计指标

4. **策略市场**
   - 分辨率：1920x1080
   - 内容：策略列表 + 排行榜

5. **多 Agent 界面**
   - 分辨率：1920x1080
   - 内容：三个 Agent 协作流程图

6. **移动端适配**
   - 分辨率：375x812（iPhone）
   - 内容：移动端界面展示

---

## 🛠️ 录制工具推荐

### 屏幕录制
- **OBS Studio** (免费，跨平台)
- **ScreenFlow** (macOS, $129)
- **Camtasia** (Windows/macOS, $249)

### GIF 制作
- **GIPHY Capture** (macOS, 免费)
- **ScreenToGif** (Windows, 免费)
- **ffmpeg + gifsicle** (命令行，免费)

### 后期编辑
- **Final Cut Pro** (macOS)
- **Adobe Premiere** (跨平台)
- **DaVinci Resolve** (免费，跨平台)

### 设计工具
- **Figma** (UI 设计)
- **Canva** (快速设计)
- **After Effects** (高级动画)

---

## 📐 技术规范

### GIF 优化
```bash
# 转换视频为 GIF
ffmpeg -i input.mov \
  -vf "fps=24,scale=1280:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" \
  -loop 0 output.gif

# 优化 GIF
gifsicle -O3 --colors 128 output.gif -o output_final.gif

# 裁剪大小
ffmpeg -i output_final.gif -ss 00:00:00 -t 00:00:20 -vf "crop=1280:720" final.gif
```

### 文件大小控制
- README 主图：< 5MB
- 教程 GIF: < 3MB
- 社交媒体：< 8MB

### 兼容性
- 支持浏览器：Chrome, Firefox, Safari, Edge
- 支持平台：GitHub, Twitter, Discord, 微信

---

## ✅ 质量检查清单

录制完成后检查：

- [ ] 画面清晰，无模糊
- [ ] 文字可读，无遮挡
- [ ] 动画流畅，无卡顿
- [ ] 颜色准确，无色差
- [ ] 文件大小符合要求
- [ ] 循环播放自然
- [ ] 无敏感信息泄露
- [ ] 拼写检查通过
- [ ] 品牌元素正确（Logo、配色）
- [ ] 在不同设备测试显示正常

---

## 📅 制作时间表

| 任务 | 负责人 | 截止日期 | 状态 |
|------|--------|---------|------|
| 脚本编写 | 文档组 | Day 3 | ✅ 完成 |
| UI 准备 | 设计组 | Day 4 | ⏳ 进行中 |
| 录制素材 | 文档组 | Day 5 | ⏳ 待开始 |
| 后期制作 | 设计组 | Day 6 | ⏳ 待开始 |
| 质量检查 | 全体 | Day 7 | ⏳ 待开始 |
| 最终发布 | 文档组 | Day 8 | ⏳ 待开始 |

---

## 📞 联系方式

**文档组负责人：**
- 📧 docs@tradeflow.ai
- 💬 Discord: #documentation

**设计组负责人：**
- 📧 design@tradeflow.ai
- 💬 Discord: #design

---

<div align="center">

**🎬 让我们一起制作惊艳的演示！**

[← 返回文档目录](README.md)

</div>
