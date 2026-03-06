# OpenFinAgent 文档站点

本目录包含 OpenFinAgent 项目的完整文档，使用 MkDocs + Material 主题构建。

## 📁 目录结构

```
docs-site/
├── docs/                      # 文档源文件
│   ├── index.md              # 首页
│   ├── getting-started.md    # 快速开始
│   ├── strategies/           # 策略文档
│   │   ├── index.md
│   │   ├── dual-ma.md
│   │   ├── momentum.md
│   │   ├── mean-reversion.md
│   │   ├── grid-trading.md
│   │   ├── ml-strategy.md
│   │   └── deep-learning.md
│   ├── api/                  # API 参考
│   │   ├── index.md
│   │   ├── trading.md
│   │   ├── data.md
│   │   └── strategy.md
│   ├── tutorials/            # 教程
│   │   ├── index.md
│   │   ├── first-strategy.md
│   │   ├── backtesting.md
│   │   └── live-trading.md
│   ├── faq.md                # 常见问题
│   └── stylesheets/          # 自定义样式
│       └── extra.css
├── mkdocs.yml                # MkDocs 配置
├── requirements.txt          # Python 依赖
└── README.md                 # 本文件
```

## 🚀 快速开始

### 1. 安装依赖

```bash
# 进入目录
cd docs-site

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 本地预览

```bash
# 启动开发服务器
mkdocs serve

# 访问 http://127.0.0.1:8000
```

### 3. 构建静态站点

```bash
# 构建站点
mkdocs build

# 输出到 site/ 目录
ls site/
```

## 🌐 部署到 GitHub Pages

### 方法 1: 使用 mike（推荐，支持版本管理）

```bash
# 安装 mike
pip install mike

# 部署到 gh-pages 分支
mike deploy --push main

# 设置默认版本
mike set-default --push main
```

### 方法 2: 使用 mkdocs gh-deploy

```bash
# 直接部署
mkdocs gh-deploy --force

# 或使用 GitHub Actions（推荐）
```

### 方法 3: GitHub Actions 自动部署

创建 `.github/workflows/deploy-docs.yml`:

```yaml
name: Deploy Docs

on:
  push:
    branches:
      - main
    paths:
      - 'docs-site/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          cd docs-site
          pip install -r requirements.txt
      
      - name: Build and deploy
        run: |
          cd docs-site
          mkdocs gh-deploy --force
```

## ⚙️ 配置说明

### mkdocs.yml 主要配置

```yaml
site_name: OpenFinAgent
site_url: https://bobipika2026.github.io/openfinagent

theme:
  name: material
  language: zh
  palette:
    - scheme: default      # 浅色模式
    - scheme: slate        # 深色模式

plugins:
  - search
  - git-revision-date-localized
  - minify
```

### 自定义样式

编辑 `docs/stylesheets/extra.css` 添加自定义样式。

## 📝 编写文档

### Markdown 语法

```markdown
# 标题
## 子标题

**粗体** *斜体*

- 列表项 1
- 列表项 2

[链接](https://example.com)

```python
# 代码块
print("Hello World")
```

!!! note "提示"
    这是提示框

```mermaid
graph LR
    A --> B
```
```

### 使用 admonitions

```markdown
!!! note "提示"
    这是提示信息

!!! warning "警告"
    这是警告信息

!!! danger "危险"
    这是危险信息
```

## 🎨 主题定制

### 颜色方案

在 `mkdocs.yml` 中配置:

```yaml
theme:
  palette:
    primary: indigo
    accent: indigo
```

可用颜色：red, pink, purple, deep-purple, indigo, blue, light-blue, cyan, teal, green, light-green, lime, yellow, amber, orange, deep-orange, brown, grey, blue-grey

### 字体配置

```yaml
theme:
  font:
    text: Roboto
    code: Roboto Mono
```

## 🔧 开发技巧

### 添加新页面

1. 在 `docs/` 目录创建 `.md` 文件
2. 在 `mkdocs.yml` 的 `nav` 中添加导航
3. 运行 `mkdocs serve` 预览

### 添加图片

```markdown
![描述](images/example.png)
```

图片文件放在 `docs/images/` 目录。

### 添加图表

使用 Mermaid:

````markdown
```mermaid
graph TB
    A --> B
    B --> C
```
````

## 📊 站点分析

### 启用分析

在 `mkdocs.yml` 中添加:

```yaml
extra:
  analytics:
    provider: google
    property: G-XXXXXXXXXX
```

## 🐛 常见问题

### Q: 中文搜索不工作？

确保安装了中文支持:

```yaml
plugins:
  - search:
      lang: zh
```

### Q: 构建失败？

检查依赖版本:

```bash
pip install -r requirements.txt --upgrade
```

### Q: 样式不生效？

清除缓存:

```bash
mkdocs build --clean
```

## 📚 相关资源

- [MkDocs 官方文档](https://www.mkdocs.org/)
- [Material 主题文档](https://squidfunk.github.io/mkdocs-material/)
- [Markdown 语法指南](https://commonmark.org/help/)
- [Mermaid 图表](https://mermaid.js.org/)

## 🤝 贡献

欢迎贡献文档！

1. Fork 项目
2. 创建分支 (`git checkout -b feature/docs-improvement`)
3. 提交更改 (`git commit -m 'Add some docs'`)
4. 推送到分支 (`git push origin feature/docs-improvement`)
5. 提交 Pull Request

## 📄 许可证

与主项目相同。

---

_最后更新：2026 年 3 月_
