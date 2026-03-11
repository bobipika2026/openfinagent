# UI 自动化测试工具使用指南

**版本**: v1.0  
**创建时间**: 2026-03-11  
**位置**: `tests/ui_automation_test.py`

---

## 📋 简介

OpenFinAgent UI 自动化测试工具用于实际测试 Web UI 功能，确保用户能够正常使用系统。

**测试范围**:
- ✅ 策略创建流程
- ✅ 策略预览功能
- ✅ 选股引擎
- ✅ 监控中心
- ✅ 通知服务

---

## 🚀 快速开始

### 1. 启动 Web UI

```bash
cd /root/.openclaw/workspace/projects/tradeflow-ai/web
streamlit run app.py --server.address=0.0.0.0 --server.port=8501
```

确保 Web UI 在 http://localhost:8501 正常运行。

### 2. 运行测试

```bash
cd /root/.openclaw/workspace/projects/tradeflow-ai
python3 tests/ui_automation_test.py
```

### 3. 查看结果

测试完成后会显示：
- 测试总数
- 通过/失败数量
- 通过率
- 详细测试结果

测试报告会保存到：`release/UI_AUTOMATION_TEST_REPORT.md`

---

## 📊 测试用例

### 1. 策略创建流程

**测试内容**:
- 使用自然语言创建策略
- 验证策略 ID、名称、代码
- 验证策略类型识别

**预期结果**:
- ✅ 策略创建成功
- ✅ 策略代码符合语法
- ✅ 策略类型正确识别

### 2. 策略预览功能

**测试内容**:
- 验证策略对象属性
- 验证策略代码语法
- 验证代码完整性

**预期结果**:
- ✅ 所有属性可访问
- ✅ 代码语法正确
- ✅ 代码长度合理

### 3. 选股引擎

**测试内容**:
- 创建选股条件
- 创建股票池
- 验证股票池数据

**预期结果**:
- ✅ 选股条件配置正确
- ✅ 股票池创建成功
- ✅ 股票数据完整

### 4. 监控中心

**测试内容**:
- 初始化监控中心
- 获取任务列表
- 初始化信号检测器

**预期结果**:
- ✅ 监控中心正常初始化
- ✅ 任务列表可获取
- ✅ 信号检测器可用

### 5. 通知服务

**测试内容**:
- 创建通知对象
- 验证通知属性
- 验证通知内容

**预期结果**:
- ✅ 通知创建成功
- ✅ 通知 ID 唯一
- ✅ 通知内容正确

---

## 📈 测试结果示例

```
============================================================
  OpenFinAgent Web UI 自动化测试工具
============================================================

[18:46:38] 🚀 开始 UI 自动化测试
[18:46:38] 🤖 测试策略创建流程
[18:46:38] ✅ 策略创建成功：自定义策略 (0.50s)
[18:46:38] 📋 测试策略预览功能
[18:46:38] ✅ 策略预览正常 (0.00s)
[18:46:38] 📈 测试选股引擎
[18:46:38] ✅ 选股引擎正常 (0.08s)
[18:46:38] 🔔 测试监控中心
[18:46:38] ✅ 监控中心正常 (0.02s)
[18:46:38] 📱 测试通知服务
[18:46:38] ✅ 通知服务正常 (0.16s)

============================================================
UI 自动化测试报告
============================================================
测试总数：5
通过：5 ✅
失败：0 ❌
通过率：100.0%
耗时：0.76 秒
============================================================

详细测试结果:
1. ✅ 策略创建流程：策略 ID: d64f7e60-5024-431c-b508-165b46603121
2. ✅ 策略预览功能：代码长度：3960 字符
3. ✅ 选股引擎：股票池：UI 测试股票池
4. ✅ 监控中心：当前任务数：0
5. ✅ 通知服务：通知 ID: 7b9cb209-36ba-4259-9500-3963fc3240f8

🎉 测试通过！系统可以正常运行
```

---

## 🔧 自定义测试

### 添加新测试用例

在 `WebUITest` 类中添加新方法：

```python
def test_your_feature(self) -> TestResult:
    """测试你的功能"""
    start = time.time()
    try:
        self.log("🔍 测试你的功能")
        
        # 测试逻辑
        # ...
        
        duration = time.time() - start
        self.log(f"✅ 测试通过 ({duration:.2f}s)")
        
        return TestResult(
            name="你的功能",
            passed=True,
            message="描述信息",
            duration=duration
        )
        
    except Exception as e:
        self.log(f"❌ 测试失败：{e}")
        return TestResult(
            name="你的功能",
            passed=False,
            message=str(e),
            duration=time.time() - start
        )
```

在 `run_all_tests()` 方法中注册：

```python
self.report.add_result(self.test_your_feature())
```

---

## 🎯 最佳实践

### 1. 测试独立性

每个测试用例应该独立运行，不依赖其他测试的结果。

```python
# ✅ 好的做法
def test_feature_a(self):
    # 自己准备数据
    data = self.prepare_data()
    # 测试...

# ❌ 不好的做法
def test_feature_a(self):
    # 依赖其他测试的结果
    data = self.session.get('other_test_data')
    # 测试...
```

### 2. 清理测试数据

测试完成后清理产生的数据：

```python
def test_stock_pool(self):
    try:
        # 创建测试数据
        pool = manager.create_pool(...)
        
        # 测试...
        
    finally:
        # 清理测试数据
        manager.delete_pool("测试股票池")
```

### 3. 合理的超时设置

为网络请求和耗时操作设置超时：

```python
response = requests.get(url, timeout=10)  # 10 秒超时
```

### 4. 详细的错误信息

提供清晰的错误信息，便于定位问题：

```python
# ✅ 好的做法
return TestResult(
    name="策略创建",
    passed=False,
    message=f"策略 ID 为空，result={result}"
)

# ❌ 不好的做法
return TestResult(
    name="策略创建",
    passed=False,
    message="失败"
)
```

---

## 📊 持续集成

### 在 CI/CD 中使用

```yaml
# .github/workflows/test.yml
name: UI Automation Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Start Web UI
        run: |
          cd web
          streamlit run app.py &
          sleep 10
      
      - name: Run UI Tests
        run: python3 tests/ui_automation_test.py
      
      - name: Upload Test Report
        uses: actions/upload-artifact@v2
        with:
          name: test-report
          path: release/UI_AUTOMATION_TEST_REPORT.md
```

---

## 🐛 故障排查

### 问题 1: Web UI 未启动

**错误**: `Connection refused`

**解决**:
```bash
# 检查 Web UI 是否运行
ps aux | grep streamlit

# 启动 Web UI
cd web && streamlit run app.py
```

### 问题 2: 测试超时

**错误**: `TimeoutError`

**解决**:
- 检查网络连接
- 增加超时时间
- 检查服务器性能

### 问题 3: 测试失败

**错误**: 某个测试用例失败

**解决**:
1. 查看详细错误信息
2. 复现问题
3. 修复后重新运行测试

---

## 📚 相关文档

- [全场景集成测试](../release/FULL_INTEGRATION_TEST_REPORT.md)
- [UI/UX 评估报告](../docs/UI_UX_EVALUATION.md)
- [用户快速开始](../docs/QUICKSTART_USER_GUIDE.md)

---

**最后更新**: 2026-03-11  
**维护者**: OpenFinAgent Team
