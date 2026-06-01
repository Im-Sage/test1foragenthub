"""归并排序测试用例集"""

import pytest
import time
from src.merge_sort import merge_sort


@pytest.mark.parametrize("input_arr, expected", [
    ([], []),
    ([5], [5]),
    ([3, 1, 2], [1, 2, 3]),
    ([5, 4, 3, 2, 1], [1, 2, 3, 4, 5]),
    ([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]),          # 已排序
    ([-3, -1, -2, 0, 5], [-3, -2, -1, 0, 5]),    # 含负数
    ([1.5, -0.5, 0.0, 2.1], [-0.5, 0.0, 1.5, 2.1]), # 浮点数
    ([2, 2, 2, 1, 1], [1, 1, 2, 2, 2]),          # 全重复
])
def test_basic_sorting(input_arr, expected):
    assert merge_sort(input_arr) == expected


def test_stability():
    """验证排序稳定性（相等元素保持原始相对顺序）"""
    items = [(3, "a"), (1, "x"), (3, "b"), (1, "y"), (3, "c")]
    result = merge_sort(items)
    assert result == [(1, "x"), (1, "y"), (3, "a"), (3, "b"), (3, "c")]


@pytest.mark.parametrize("invalid_input", ["string", 123, None, {1, 2}])
def test_type_error(invalid_input):
    with pytest.raises(TypeError, match="输入必须是列表或元组"):
        merge_sort(invalid_input)


def test_uncomparable_elements():
    """Python 3 默认拒绝跨类型比较，应抛出 TypeError"""
    with pytest.raises(TypeError):
        merge_sort([1, "two", 3])


def test_large_input_performance():
    """10 万逆序数据排序应在 2s 内完成，验证 O(n log n) 复杂度与内存优化"""
    arr = list(range(100_000, 0, -1))
    start = time.perf_counter()
    result = merge_sort(arr)
    elapsed = time.perf_counter() - start

    assert result == sorted(arr)
    assert elapsed < 2.0, f"排序耗时过长: {elapsed:.3f}s"


def test_original_array_unchanged():
    """确保不修改原始输入数据"""
    original = [4, 2, 1, 3]
    merge_sort(original)
    assert original == [4, 2, 1, 3]