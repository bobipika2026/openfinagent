"""
策略解析器 - 将自然语言转换为策略参数
"""

import re
from typing import Dict, List, Optional
import jieba


class StrategyParser:
    """策略自然语言解析器"""

    def __init__(self):
        # 策略类型关键词映射
        self.strategy_keywords = {
            '均线交叉': 'ma_cross',
            '均线': 'ma_cross',
            'ma': 'ma_cross',
            '动量': 'momentum',
            'momentum': 'momentum',
            '趋势': 'momentum',
        }

        # 参数提取规则
        self.param_patterns = {
            'short_window': [r'(\d+)\s*日\s*均线', r'短周期\s*(\d+)', r'快线\s*(\d+)'],
            'long_window': [r'(\d+)\s*日\s*均线.*?(\d+)\s*日', r'长周期\s*(\d+)', r'慢线\s*(\d+)'],
            'lookback_period': [r'看\s*(\d+)\s*[天日]', r'周期\s*(\d+)', r'回溯\s*(\d+)'],
            'threshold': [r'阈值\s*(\d+\.?\d*)%', r'超过\s*(\d+\.?\d*)%'],
            'initial_capital': [r'资金\s*(\d+\.?\d*)\s*[万千]', r'本金\s*(\d+\.?\d*)\s*[万千]'],
        }

    def parse(self, text: str) -> Dict:
        """
        解析自然语言描述

        Args:
            text: 策略描述文本

        Returns:
            解析后的参数字典
        """
        result = {
            'strategy_type': 'ma_cross',  # 默认
            'params': {},
            'name': '自定义策略',
            'initial_capital': 100000.0,
        }

        # 检测策略类型
        result['strategy_type'] = self._detect_strategy_type(text)

        # 提取参数
        params = self._extract_parameters(text)
        result['params'].update(params)

        # 提取初始资金
        capital = self._extract_capital(text)
        if capital:
            result['initial_capital'] = capital

        # 提取策略名称
        name = self._extract_name(text)
        if name:
            result['name'] = name

        return result

    def _detect_strategy_type(self, text: str) -> str:
        """检测策略类型"""
        text_lower = text.lower()
        for keyword, strategy_type in self.strategy_keywords.items():
            if keyword in text_lower:
                return strategy_type
        return 'ma_cross'

    def _extract_parameters(self, text: str) -> Dict:
        """提取策略参数"""
        params = {}

        # 提取均线周期
        ma_pattern = r'(\d+)\s*[日天]均线.*?(\d+)\s*[日天]均线'
        match = re.search(ma_pattern, text)
        if match:
            params['short_window'] = int(match.group(1))
            params['long_window'] = int(match.group(2))
        else:
            # 单个均线周期
            single_ma = re.search(r'(\d+)\s*[日天]均线', text)
            if single_ma:
                params['short_window'] = int(single_ma.group(1))

        # 提取动量周期
        momentum_pattern = r'看\s*(\d+)\s*[天日]'
        match = re.search(momentum_pattern, text)
        if match:
            params['lookback_period'] = int(match.group(1))

        # 提取阈值
        threshold_pattern = r'(\d+\.?\d*)\s*%'
        match = re.search(threshold_pattern, text)
        if match:
            params['threshold'] = float(match.group(1)) / 100

        return params

    def _extract_capital(self, text: str) -> Optional[float]:
        """提取初始资金"""
        # 匹配 "10 万元"、"5 万"、"100 万" 等
        pattern = r'(\d+\.?\d*)\s*[万千]'
        match = re.search(pattern, text)
        if match:
            value = float(match.group(1))
            if '万' in text[match.start():match.end()]:
                return value * 10000
            elif '千' in text[match.start():match.end()]:
                return value * 1000
        return None

    def _extract_name(self, text: str) -> Optional[str]:
        """提取策略名称"""
        pattern = r'策略名称 [:：]?\s*(.+?)(?:\n|$)'
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
        return None

    def validate(self, text: str) -> Dict:
        """
        验证策略描述的完整性

        Args:
            text: 策略描述

        Returns:
            验证结果
        """
        issues = []
        parsed = self.parse(text)

        if 'short_window' not in parsed['params']:
            issues.append("未指定短期均线周期")
        if 'long_window' not in parsed['params']:
            issues.append("未指定长期均线周期")

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'parsed': parsed
        }
