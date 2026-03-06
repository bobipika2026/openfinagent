# OpenFinAgent 架构文档

本目录包含 OpenFinAgent 项目的完整技术架构设计文档。

## 📁 文档列表

| 文档 | 说明 | 大小 |
|------|------|------|
| [system-architecture.md](system-architecture.md) | 系统架构设计 - 模块划分、数据流、扩展性 | ~15KB |
| [tech-stack.md](tech-stack.md) | 技术栈选型 - 语言、框架、依赖库 | ~7KB |
| [api-design.md](api-design.md) | API 设计规范 - 核心 API、策略开发、CLI | ~11KB |
| [database-design.md](database-design.md) | 数据库设计 - 存储方案、Schema、缓存策略 | ~12KB |
| [deployment.md](deployment.md) | 部署方案 - 包分发、Docker、K8s、CI/CD | ~16KB |

## 🎯 架构亮点

1. **自然语言驱动**: NLP 解析器将中文策略描述转换为可执行代码
2. **模块化设计**: 清晰的 4 层架构 (用户接口→应用服务→核心引擎→数据访问)
3. **零依赖部署**: v0.1-v0.3 阶段仅需 Python 环境，无需服务器
4. **可扩展架构**: 支持自定义策略、指标、数据源插件化扩展
5. **云原生规划**: Phase 3 支持 Kubernetes、微服务、多租户

## 📊 技术栈概览

| 层级 | 技术选型 |
|------|----------|
| **核心语言** | Python 3.9+ |
| **数据处理** | pandas, numpy, ta-lib |
| **NLP** | jieba, HanLP (可选) |
| **可视化** | matplotlib, seaborn, mplfinance |
| **数据源** | AKShare (A 股), yfinance (美股), ccxt (加密货币) |
| **数据库** (Phase 2) | PostgreSQL + TimescaleDB + Redis |
| **部署** | PyPI → Docker → Kubernetes |

## 🚀 版本规划

| 版本 | 阶段 | 架构重点 |
|------|------|----------|
| v0.1-v0.3 | MVP | Python 包分发、本地存储 |
| v0.5 | Web 平台 | FastAPI + React + PostgreSQL |
| v1.0 | 云原生 | Kubernetes + 微服务 + 多租户 |

## 📝 更新记录

- **2026-03-06**: 初始架构设计完成

---

*OpenFinAgent - 用自然语言写量化策略*
