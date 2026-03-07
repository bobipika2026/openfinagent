# 🔐 重新生成 GitHub Token（需要 workflow 权限）

## 问题

当前 Token 缺少 `workflow` 权限，无法推送 GitHub Actions 配置文件。

---

## ✅ 正确步骤

### 1. 访问 Token 创建页面

https://github.com/settings/tokens/new

### 2. 填写信息

| 字段 | 值 |
|------|-----|
| **Note** | `OpenFinAgent Full Access` |
| **Expiration** | `No expiration` |
| **Scopes** | 勾选以下权限 |

### 3. 必须勾选的权限

- ✅ **repo** (全部 5 个子权限)
- ✅ **workflow** ← 这个是关键！
- ✅ **delete_repo** (可选，用于清理)
- ✅ **admin:org** (可选)

### 4. 生成并复制

点击 **Generate token** → 复制新 Token（`ghp_xxxxxxxxxxxx`）

---

## ⚡ 快速方案：只推送代码（不含 workflow）

如果不想重新生成 Token，可以先推送代码，workflow 文件稍后手动添加：

```bash
cd /root/.openclaw/workspace/openfinagent

# 暂时移除 workflow 文件
mv .github/workflows/ci-cd.yml /tmp/ci-cd.yml.bak

# 推送
git push -f -u origin main

# 恢复文件
mv /tmp/ci-cd.yml.bak .github/workflows/ci-cd.yml
```

**缺点**: GitHub Actions 需要手动配置

---

## 🎯 推荐：重新生成完整权限 Token

**新 Token 生成后，执行：**

```bash
cd /root/.openclaw/workspace/openfinagent
git remote remove origin
git remote add origin https://ghp_NEW_TOKEN@github.com/bobipika2026/openfinagent.git
git push -f -u origin main
```

---

**请告诉我：选择哪个方案？**
1. 重新生成完整权限 Token（推荐）
2. 先推送代码，workflow 稍后手动添加
