# 策略工厂 Bug 修复报告

**问题**: 创建策略时报错 `Can't instantiate abstract class BaseStrategy`

**原因分析**:
1. 策略代码生成器生成的代码使用 `from strategy.base import BaseStrategy`
2. 动态加载模块时，Python 无法找到正确的 `strategy.base` 模块
3. 导致加载的 `BaseStrategy` 是抽象类，而不是实际的基类

**解决方案**:

## 方案 1: 修改生成器 (推荐)

修改 `src/strategy_factory/generator.py`，在生成的代码中添加正确的导入路径：

```python
def _get_ma_cross_template(self, params, name, initial_capital):
    # 在生成的代码开头添加路径设置
    code = f'''"""
{name} - 均线交叉策略
"""

import sys
import os
# 自动添加项目路径
_current_dir = os.path.dirname(os.path.abspath(__file__))
for _parent in [_current_dir] + [os.path.dirname(_current_dir)] * 3:
    if os.path.exists(os.path.join(_parent, 'src')):
        _src_path = os.path.join(_parent, 'src')
        if _src_path not in sys.path:
            sys.path.insert(0, _src_path)
        break

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime

from strategy.base import BaseStrategy

# ... 剩余代码
'''
```

## 方案 2: 修改工厂加载逻辑

修改 `src/strategy_factory/factory.py` 的 `_load_strategy_class` 方法，在加载前设置正确的 `sys.path`：

```python
def _load_strategy_class(self, code: str, name: str):
    import sys
    # 添加项目根目录和 src 到路径
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src_path = os.path.join(project_root, 'src')
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    # ... 剩余代码
```

## 方案 3: 使用 exec 直接执行 (临时方案)

不动态加载模块，而是直接在当前命名空间执行策略代码：

```python
def _create_strategy_instance(self, code: str, name: str):
    # 在当前命名空间执行代码
    namespace = {
        'pd': __import__('pandas'),
        'np': __import__('numpy'),
        'BaseStrategy': __import__('src.strategy.base', fromlist=['BaseStrategy']).BaseStrategy,
        # ... 其他依赖
    }
    exec(code, namespace)
    
    # 查找策略类
    for name, obj in namespace.items():
        if isinstance(obj, type) and name.endswith('Strategy') and name != 'BaseStrategy':
            return obj
```

**建议**: 采用方案 1，修改生成器，让生成的代码自带路径设置，这样最通用。

**测试命令**:
```bash
cd /root/.openclaw/workspace/projects/tradeflow-ai
python3 -c "
from src.strategy_factory import StrategyFactory
factory = StrategyFactory()
result = factory.create_from_natural_language(
    description='当 5 日均线上穿 20 日均线时买入，下穿时卖出',
    auto_backtest=True
)
print(f'✅ 成功：{result.name}, 评分：{result.backtest_report.get(\"score\")}')
"
```

**预计修复时间**: 10 分钟
**影响范围**: 策略工厂模块
**风险评估**: 低 - 只影响策略创建功能
