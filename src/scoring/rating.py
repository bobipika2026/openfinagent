"""
评级系统模块

实现回测评分的等级评定功能，将综合评分转换为 S/A/B/C/D 等级。
符合证券行业策略评估标准。
"""

from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum


class RatingLevel(Enum):
    """评级等级枚举"""
    S = "S"  # 优秀 (>=90 分)
    A = "A"  # 良好 (>=80 分)
    B = "B"  # 中等 (>=70 分)
    C = "C"  # 及格 (>=60 分)
    D = "D"  # 不及格 (<60 分)


@dataclass
class RatingResult:
    """评级结果数据类"""
    level: RatingLevel
    score: float
    description: str
    is_pass: bool

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'level': self.level.value,
            'score': round(self.score, 2),
            'description': self.description,
            'is_pass': self.is_pass,
        }


class RatingSystem:
    """
    评级系统

    根据综合评分确定策略等级，提供证券行业标准的评级体系。
    支持自定义评级阈值。
    """

    # 默认评级阈值
    DEFAULT_THRESHOLDS = {
        RatingLevel.S: 90.0,  # 优秀
        RatingLevel.A: 80.0,  # 良好
        RatingLevel.B: 70.0,  # 中等
        RatingLevel.C: 60.0,  # 及格
        RatingLevel.D: 0.0,   # 不及格
    }

    # 评级描述
    RATING_DESCRIPTIONS = {
        RatingLevel.S: "优秀 - 策略表现卓越，强烈推荐",
        RatingLevel.A: "良好 - 策略表现稳定，推荐",
        RatingLevel.B: "中等 - 策略表现一般，可考虑",
        RatingLevel.C: "及格 - 策略表现勉强，需谨慎",
        RatingLevel.D: "不及格 - 策略表现差，不推荐",
    }

    def __init__(self, thresholds: Optional[Dict[RatingLevel, float]] = None):
        """
        初始化评级系统

        Args:
            thresholds: 自定义评级阈值字典，如不传则使用默认阈值

        Example:
            >>> rating = RatingSystem()
            >>> result = rating.get_rating(85.5)
            >>> result.level
            <RatingLevel.A: 'A'>
        """
        self.thresholds = thresholds or self.DEFAULT_THRESHOLDS.copy()
        self._validate_thresholds()

    def _validate_thresholds(self):
        """验证阈值的有效性"""
        # 按阈值从高到低排序 (S 级最高，D 级最低)
        sorted_levels = sorted(
            self.thresholds.keys(),
            key=lambda x: self.thresholds[x],
            reverse=True,
        )

        for i in range(len(sorted_levels) - 1):
            current_level = sorted_levels[i]
            next_level = sorted_levels[i + 1]

            if self.thresholds[current_level] < self.thresholds[next_level]:
                raise ValueError(
                    f"阈值配置错误：{current_level.value}级阈值 "
                    f"({self.thresholds[current_level]}) 不能小于 "
                    f"{next_level.value}级阈值 ({self.thresholds[next_level]})"
                )

    def get_level(self, score: float) -> RatingLevel:
        """
        根据评分获取评级等级

        Args:
            score: 综合评分 (0-100)

        Returns:
            评级等级

        Example:
            >>> rating = RatingSystem()
            >>> rating.get_level(92.5)
            <RatingLevel.S: 'S'>
            >>> rating.get_level(75.0)
            <RatingLevel.B: 'B'>
        """
        if score < 0 or score > 100:
            raise ValueError(f"评分必须在 0-100 之间，当前评分：{score}")

        for level in [RatingLevel.S, RatingLevel.A, RatingLevel.B, RatingLevel.C, RatingLevel.D]:
            if score >= self.thresholds[level]:
                return level

        return RatingLevel.D

    def get_rating(self, score: float) -> RatingResult:
        """
        获取完整的评级结果

        Args:
            score: 综合评分 (0-100)

        Returns:
            包含等级、评分、描述的评级结果

        Example:
            >>> rating = RatingSystem()
            >>> result = rating.get_rating(85.5)
            >>> result.level.value
            'A'
            >>> result.is_pass
            True
        """
        level = self.get_level(score)
        description = self.RATING_DESCRIPTIONS[level]
        is_pass = level in [RatingLevel.S, RatingLevel.A, RatingLevel.B, RatingLevel.C]

        return RatingResult(
            level=level,
            score=score,
            description=description,
            is_pass=is_pass,
        )

    def get_level_description(self, level: RatingLevel) -> str:
        """
        获取评级等级的描述

        Args:
            level: 评级等级

        Returns:
            等级描述
        """
        return self.RATING_DESCRIPTIONS.get(level, "未知等级")

    def is_passing(self, score: float) -> bool:
        """
        判断评分是否及格

        Args:
            score: 综合评分

        Returns:
            是否及格 (C 级及以上为及格)
        """
        level = self.get_level(score)
        return level != RatingLevel.D

    def get_threshold(self, level: RatingLevel) -> float:
        """
        获取指定等级的阈值

        Args:
            level: 评级等级

        Returns:
            该等级的最低分数要求
        """
        return self.thresholds.get(level, 0.0)

    def set_threshold(self, level: RatingLevel, threshold: float):
        """
        设置指定等级的阈值

        Args:
            level: 评级等级
            threshold: 新的阈值

        Raises:
            ValueError: 阈值配置冲突时
        """
        self.thresholds[level] = threshold
        self._validate_thresholds()

    def get_rating_distribution(self, scores: list) -> Dict[str, int]:
        """
        统计评分分布

        Args:
            scores: 评分列表

        Returns:
            各等级的数量统计
        """
        distribution = {level.value: 0 for level in RatingLevel}

        for score in scores:
            level = self.get_level(score)
            distribution[level.value] += 1

        return distribution

    def get_pass_rate(self, scores: list) -> float:
        """
        计算通过率

        Args:
            scores: 评分列表

        Returns:
            通过率 (百分比形式)
        """
        if not scores:
            return 0.0

        passing_count = sum(1 for score in scores if self.is_passing(score))
        return round((passing_count / len(scores)) * 100, 2)

    def to_dict(self) -> Dict:
        """
        将评级系统配置转换为字典

        Returns:
            包含阈值配置的字典
        """
        return {
            'thresholds': {
                level.value: threshold
                for level, threshold in self.thresholds.items()
            },
            'descriptions': {
                level.value: desc
                for level, desc in self.RATING_DESCRIPTIONS.items()
            },
        }
