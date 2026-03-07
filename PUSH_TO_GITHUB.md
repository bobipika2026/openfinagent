# 🔐 GitHub SSH 推送配置指南

## 问题诊断

HTTPS 推送失败，需要配置 SSH 密钥或使用 Personal Access Token。

---

## 方案一：配置 SSH 密钥（推荐，一劳永逸）

### 1. 生成 SSH 密钥

```bash
ssh-keygen -t ed25519 -C "hi@openfinagent.ai"
# 按 Enter 接受默认路径
# 按 Enter 跳过密码（或设置密码更安全）
```

### 2. 查看并复制公钥

```bash
cat ~/.ssh/id_ed25519.pub
# 复制输出内容（以 ssh-ed25519 开头）
```

### 3. 添加到 GitHub

1. 访问 https://github.com/settings/keys
2. 点击 **New SSH key**
3. **Title**: `OpenFinAgent Deployment`
4. **Key type**: ✅ Authentication Key
5. **Key**: 粘贴刚才复制的公钥内容
6. 点击 **Add SSH key**

### 4. 切换远程仓库为 SSH

```bash
cd /root/.openclaw/workspace/openfinagent
git remote set-url origin git@github.com:bobipika2026/openfinagent.git
git remote -v
# 确认显示 git@github.com:bobipika2026/openfinagent.git
```

### 5. 推送代码

```bash
git push -u origin main
```

---

## 方案二：使用 Personal Access Token（快速，无需 SSH）

### 1. 创建 Token

1. 访问 https://github.com/settings/tokens/new
2. **Note**: `OpenFinAgent Deployment`
3. **Expiration**: `90 days` 或 `No expiration`
4. **Scopes**: ✅ 勾选 `repo`（完整控制仓库）
5. 点击 **Generate token**
6. **复制 Token**（只显示一次！格式如 `ghp_xxxxxxxxxxxx`）

### 2. 使用 Token 推送

```bash
cd /root/.openclaw/workspace/openfinagent

# 移除现有远程
git remote remove origin

# 添加带 Token 的远程（替换 YOUR_TOKEN）
git remote add origin https://ghp_YOUR_TOKEN@github.com/bobipika2026/openfinagent.git

# 推送
git branch -M main
git push -u origin main
```

---

## 方案三：使用 Git Credential Manager（Windows/Mac）

如果你使用 Windows 或 Mac，Git 可能会自动弹出 GitHub 登录窗口。

```bash
cd /root/.openclaw/workspace/openfinagent
git push -u origin main
# 如果弹出浏览器，按提示授权即可
```

---

## ✅ 推送成功后验证

### 1. 检查 GitHub 仓库

访问 https://github.com/bobipika2026/openfinagent

确认：
- ✅ 代码已上传（显示文件列表）
- ✅ README.md 正常渲染
- ✅ 显示 1 commit

### 2. 设置仓库话题标签

1. 在 GitHub 仓库页面右侧 "About" 区域点击 ⚙️
2. 添加以下话题：

```
quantitative-trading
ai
fintech
trading-bot
python
artificial-intelligence
algorithmic-trading
stock-market
crypto
agent-framework
backtesting
open-source
```

3. 点击 **Save changes**

### 3. 设置网站和社交链接（可选）

在同一个 About 区域：
- 🌐 Website: `https://openfinagent.ai`（待创建）
- 💬 Discord: `https://discord.gg/openfinagent`（待创建）

---

## 🚨 常见问题

### 问题 1: `Permission denied (publickey)`

**原因**: SSH 密钥未正确配置

**解决**:
```bash
# 测试 SSH 连接
ssh -T git@github.com

# 如果失败，重新执行方案一的步骤 1-3
```

### 问题 2: `Authentication failed`

**原因**: Token 错误或过期

**解决**: 重新生成 Token（方案二），确保：
- Token 以 `ghp_` 开头
- 勾选了 `repo` 权限
- 复制时没有多余空格

### 问题 3: `remote origin already exists`

**原因**: 远程仓库已存在

**解决**:
```bash
git remote remove origin
git remote add origin <新的 URL>
```

---

## 📞 需要帮助？

执行以下命令，我会自动帮你配置：

```bash
# 告诉我你选择的方案（SSH / Token）
```

---

**推送成功后，我们将立即启动 60 天增长计划！🚀**
