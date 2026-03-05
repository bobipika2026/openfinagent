# TradeFlow AI - GitHub 仓库设置指南

## 已完成的工作 ✅

1. ✅ 初始化本地 git 仓库
2. ✅ 创建项目结构
3. ✅ 编写核心代码模块
4. ✅ 添加 README.md
5. ✅ 添加 MIT License
6. ✅ 首次 commit 完成

## 手动创建 GitHub 仓库步骤

### 方法一：通过 GitHub 网站（推荐）

1. 访问 https://github.com/new
2. 仓库名称：`tradeflow-ai`
3. 描述：`AI 量化交易助手 - 用自然语言写量化策略`
4. 可见性：Public
5. **不要**初始化 README、.gitignore 或 license（我们已经有了）
6. 点击 "Create repository"

### 方法二：使用 GitHub CLI（需要先安装）

```bash
# 安装 gh CLI
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh

# 认证
gh auth login

# 创建仓库
gh repo create tradeflow-ai --public --description "AI 量化交易助手 - 用自然语言写量化策略"
```

## 推送代码到 GitHub

创建仓库后，执行以下命令：

```bash
cd /root/.openclaw/workspace/tradeflow-ai

# 添加远程仓库（替换 YOUR_USERNAME 为你的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/tradeflow-ai.git

# 或者使用 SSH（如果配置了 SSH 密钥）
# git remote add origin git@github.com:YOUR_USERNAME/tradeflow-ai.git

# 推送到 GitHub
git branch -M main
git push -u origin main
```

## 设置仓库话题标签

在 GitHub 仓库页面右侧 "About" 区域，点击齿轮图标，添加：
- quantitative-trading
- ai
- trading
- python
- stock

## 启用 GitHub Pages（可选）

1. 进入仓库 Settings → Pages
2. Source: Deploy from a branch
3. Branch: main → /docs (需要先创建 docs 文件夹)
4. Save

## 项目结构

```
tradeflow-ai/
├── README.md           # 项目说明
├── LICENSE             # MIT License
├── .gitignore          # Git 忽略规则
├── setup.py            # Python 包安装配置
└── tradeflow/          # 主包
    ├── __init__.py     # 包初始化
    ├── strategy.py     # 策略模块
    ├── analyzer.py     # 分析器模块
    └── executor.py     # 执行器模块
```

## 下一步开发建议

1. 集成 AI 模型（如 Qwen）解析自然语言策略
2. 添加数据源接口（Yahoo Finance, Alpha Vantage 等）
3. 实现策略回测引擎
4. 添加实时交易执行
5. 创建文档站点

---

**仓库 URL 模板**: `https://github.com/YOUR_USERNAME/tradeflow-ai`
