# GitHub Pages 部署配置 - OpenFinAgent

**目标**: 部署专业的项目文档站点

---

## 📋 部署步骤

### 1. 创建 gh-pages 分支

```bash
# 创建并切换到 gh-pages 分支
git checkout --orphan gh-pages
git reset --hard

# 创建初始文件
echo "# OpenFinAgent Documentation" > index.md
git add index.md
git commit -m "Initial gh-pages commit"
git push origin gh-pages
```

### 2. 配置 MkDocs

```bash
# 安装 MkDocs
pip install mkdocs mkdocs-material

# 创建 mkdocs.yml
```

### 3. 创建 mkdocs.yml

```yaml
site_name: OpenFinAgent
site_description: AI-Powered Quantitative Trading Platform
site_url: https://bobipika2026.github.io/openfinagent

repo_name: bobipika2026/openfinagent
repo_url: https://github.com/bobipika2026/openfinagent

theme:
  name: material
  palette:
    primary: blue
    accent: indigo
  features:
    - navigation.tabs
    - navigation.sections
    - navigation.expand
    - search.suggest
    - search.highlight

nav:
  - Home: index.md
  - Quick Start: quickstart.md
  - Documentation:
    - Architecture: architecture.md
    - Strategies: strategies.md
    - Data Sources: data-sources.md
    - Backtesting: backtesting.md
    - Web UI: web-ui.md
  - Examples:
    - Basic Strategy: examples/basic.md
    - Advanced Strategy: examples/advanced.md
    - Data Import: examples/data-import.md
  - API Reference:
    - Core API: api/core.md
    - Strategies API: api/strategies.md
    - Data API: api/data.md
  - Contributing: contributing.md

markdown_extensions:
  - pymdownx.highlight
  - pymdownx.superfences
  - toc:
      permalink: true

extra:
  social:
    - icon: fontawesome/brands/github
      link: https://github.com/bobipika2026/openfinagent
    - icon: fontawesome/brands/twitter
      link: https://twitter.com/openfinagent
```

### 4. 创建文档结构

```bash
mkdir -p docs/examples docs/api
```

### 5. 部署到 GitHub Pages

```bash
# 使用 MkDocs 部署
mkdocs gh-deploy --force

# 或使用 GitHub Actions (推荐)
```

---

## 🔧 GitHub Actions 自动部署

### 创建 .github/workflows/docs.yml

```yaml
name: Deploy Docs

on:
  push:
    branches:
      - main
    paths:
      - 'docs/**'
      - 'mkdocs.yml'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure Git
        run: |
          git config user.name "$GITHUB_ACTOR"
          git config user.email "$GITHUB_ACTOR@users.noreply.github.com"
      
      - name: Install MkDocs
        run: pip install mkdocs mkdocs-material
      
      - name: Deploy to GitHub Pages
        run: mkdocs gh-deploy --force
```

---

## 📄 文档页面清单

### 核心页面 (必须)
- [x] index.md - 首页
- [x] quickstart.md - 快速开始
- [x] architecture.md - 架构说明
- [ ] strategies.md - 策略文档
- [ ] data-sources.md - 数据源
- [ ] backtesting.md - 回测指南
- [ ] web-ui.md - Web UI 说明

### 示例页面
- [ ] examples/basic.md - 基础示例
- [ ] examples/advanced.md - 高级示例
- [ ] examples/data-import.md - 数据导入

### API 文档
- [ ] api/core.md - 核心 API
- [ ] api/strategies.md - 策略 API
- [ ] api/data.md - 数据 API

### 其他页面
- [x] contributing.md - 贡献指南
- [ ] changelog.md - 更新日志
- [ ] faq.md - 常见问题

---

## 🎨 自定义样式

### docs/stylesheets/extra.css

```css
:root {
  --md-primary-fg-color: #1976d2;
  --md-accent-fg-color: #3f51b5;
}

.md-header {
  background: linear-gradient(90deg, #1976d2 0%, #3f51b5 100%);
}
```

---

## 📊 访问统计

### 配置 Google Analytics

```yaml
extra:
  analytics:
    provider: google
    property: G-XXXXXXXXXX
```

---

## ✅ 检查清单

- [ ] 创建 gh-pages 分支
- [ ] 配置 MkDocs
- [ ] 创建文档结构
- [ ] 配置 GitHub Actions
- [ ] 自定义样式
- [ ] 配置分析工具
- [ ] 测试本地构建
- [ ] 首次部署
- [ ] 验证访问

---

## 🌐 访问地址

- **生产环境**: https://bobipika2026.github.io/openfinagent
- **自定义域名**: (可选) https://docs.openfinagent.io

---

**状态**: 配置完成，等待部署
