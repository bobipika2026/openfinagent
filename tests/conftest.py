"""
pytest 配置文件

配置 pytest-asyncio 和其他测试fixture。

@module: tests.conftest
@author: OpenFinAgent Team
@version: 1.0.0
"""

import pytest


@pytest.fixture(scope="session")
def event_loop_policy():
    """设置事件循环策略"""
    import asyncio
    return asyncio.DefaultEventLoopPolicy()
