"""
Analyzer 模块单元测试
测试覆盖率目标：90%+
"""

import pytest
from tradeflow.analyzer import Analyzer


class TestAnalyzerInit:
    """Analyzer 初始化测试"""

    def test_default_init(self):
        """测试默认初始化"""
        analyzer = Analyzer()
        assert analyzer.data is None

    def test_init_creates_instance(self):
        """测试创建实例"""
        analyzer = Analyzer()
        assert isinstance(analyzer, Analyzer)


class TestAnalyzerLoadData:
    """加载市场数据测试"""

    def test_load_data_basic(self, mock_analyzer):
        """测试基础数据加载"""
        result = mock_analyzer.load_data("600519.SH", "2023-01-01", "2024-01-01")
        assert result is mock_analyzer  # 支持链式调用

    def test_load_data_different_symbols(self, mock_analyzer):
        """测试不同股票代码"""
        symbols = ["600519.SH", "000001.SZ", "300750.SZ"]
        for symbol in symbols:
            result = mock_analyzer.load_data(symbol, "2023-01-01", "2024-01-01")
            assert result is mock_analyzer

    def test_load_data_chainable(self, mock_analyzer):
        """测试链式调用"""
        result = mock_analyzer.load_data("600519.SH", "2023-01-01", "2024-01-01")
        assert result is mock_analyzer


class TestAnalyzerCalculateIndicators:
    """计算技术指标测试"""

    def test_calculate_single_indicator(self, mock_analyzer):
        """测试计算单个指标"""
        mock_analyzer.load_data("600519.SH", "2023-01-01", "2024-01-01")
        result = mock_analyzer.calculate_indicators(["MA5"])
        assert result is mock_analyzer

    def test_calculate_multiple_indicators(self, mock_analyzer):
        """测试计算多个指标"""
        mock_analyzer.load_data("600519.SH", "2023-01-01", "2024-01-01")
        indicators = ["MA5", "MA20", "MACD", "RSI"]
        result = mock_analyzer.calculate_indicators(indicators)
        assert result is mock_analyzer

    def test_calculate_indicators_chainable(self, mock_analyzer):
        """测试链式调用"""
        mock_analyzer.load_data("600519.SH", "2023-01-01", "2024-01-01")
        result = mock_analyzer.calculate_indicators(["MA5"]).calculate_indicators(["MA20"])
        assert result is mock_analyzer


class TestAnalyzerAnalyze:
    """执行分析测试"""

    def test_analyze_basic(self, mock_analyzer):
        """测试基础分析"""
        mock_analyzer.load_data("600519.SH", "2023-01-01", "2024-01-01")
        result = mock_analyzer.analyze()
        assert isinstance(result, dict)
        assert "trend" in result
        assert "volatility" in result
        assert "volume_trend" in result

    def test_analyze_returns_metrics(self, mock_analyzer):
        """测试分析返回指标"""
        mock_analyzer.load_data("600519.SH", "2023-01-01", "2024-01-01")
        result = mock_analyzer.analyze()
        assert all(key in result for key in [
            "trend",
            "volatility",
            "volume_trend"
        ])

    def test_analyze_without_loading_data(self):
        """测试未加载数据时分析"""
        analyzer = Analyzer()
        result = analyzer.analyze()
        assert isinstance(result, dict)


class TestAnalyzerWorkflow:
    """Analyzer 工作流测试"""

    def test_full_workflow(self):
        """测试完整工作流"""
        analyzer = Analyzer()
        analyzer.load_data("600519.SH", "2023-01-01", "2024-01-01")
        analyzer.calculate_indicators(["MA5", "MA20", "MACD"])
        result = analyzer.analyze()
        assert isinstance(result, dict)

    def test_chained_workflow(self):
        """测试链式工作流"""
        analyzer = Analyzer()
        result = (analyzer
                  .load_data("600519.SH", "2023-01-01", "2024-01-01")
                  .calculate_indicators(["MA5", "MA20"])
                  .analyze())
        assert isinstance(result, dict)


class TestAnalyzerEdgeCases:
    """边界情况测试"""

    def test_empty_indicators_list(self, mock_analyzer):
        """测试空指标列表"""
        mock_analyzer.load_data("600519.SH", "2023-01-01", "2024-01-01")
        result = mock_analyzer.calculate_indicators([])
        assert result is mock_analyzer

    def test_multiple_load_data_calls(self, mock_analyzer):
        """测试多次加载数据"""
        mock_analyzer.load_data("600519.SH", "2023-01-01", "2024-01-01")
        mock_analyzer.load_data("000001.SZ", "2023-01-01", "2024-01-01")
        result = mock_analyzer.analyze()
        assert isinstance(result, dict)
