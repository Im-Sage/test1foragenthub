import pytest
import sys
import os

# 适配实际项目路径，请根据真实结构修改
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.sorting import quick_sort


class TestSortingAlgorithm:
    """排序算法单元测试集"""

    @pytest.mark.parametrize("input_arr, expected, test_id", [
        pytest.param([], [], "empty_array"),
        pytest.param([42], [42], "single_element"),
        pytest.param([1, 2, 3, 4, 5], [1, 2, 3, 4, 5], "already_sorted"),
        pytest.param([5, 4, 3, 2, 1], [1, 2, 3, 4, 5], "reverse_sorted"),
        pytest.param([3, 1, 2, 3, 1, 2], [1, 1, 2, 2, 3, 3], "duplicates"),
        pytest.param([-3, -1, 0, 2, -2, 1], [-3, -2, -1, 0, 1, 2], "mixed_signs"),
    ])
    def test_core_scenarios(self, input_arr, expected, test_id):
        """覆盖空数组、单元素、已排序、逆序、重复元素等核心分支"""
        assert quick_sort(input_arr) == expected, f"Failed on case: {test_id}"

    def test_type_error_branch(self):
        """覆盖异常输入分支"""
        with pytest.raises(TypeError, match="输入必须为列表类型"):
            quick_sort(None)
        with pytest.raises(TypeError, match="输入必须为列表类型"):
            quick_sort("string")

    def test_immutability(self):
        """验证算法是否为纯函数（不修改原数组）"""
        original = [3, 1, 4, 1, 5]
        snapshot = original.copy()
        quick_sort(original)
        assert original == snapshot, "原数组被意外修改，算法非纯函数"

    def test_large_scale_consistency(self):
        """大数据量与内置 sorted 结果一致性验证"""
        import random
        arr = [random.randint(-1000, 1000) for _ in range(200)]
        assert quick_sort(arr) == sorted(arr)