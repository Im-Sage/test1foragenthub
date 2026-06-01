"""快速排序单元测试与覆盖验证。"""

import random
import pytest
from typing import List

from src.algorithms.quick_sort import quick_sort


@pytest.mark.parametrize(
    "input_arr, expected",
    [
        ([], []),
        ([1], [1]),
        ([3, 1, 2], [1, 2, 3]),
        ([5, 5, 5, 5], [5, 5, 5, 5]),
        ([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]),
        ([5, 4, 3, 2, 1], [1, 2, 3, 4, 5]),
        ([-1, -3, 0, 2, -5], [-5, -3, -1, 0, 2]),
        (list(range(100)), list(range(100))),
    ],
)
def test_quick_sort_correctness(input_arr: List[int], expected: List[int]) -> None:
    arr_copy = input_arr.copy()
    result = quick_sort(arr_copy)
    assert result == expected
    assert result is arr_copy  # 验证原地修改


def test_quick_sort_inplace_mutation() -> None:
    arr = [9, 2, 5, 1]
    original_id = id(arr)
    quick_sort(arr)
    assert id(arr) == original_id
    assert arr == [1, 2, 5, 9]


@pytest.mark.parametrize("invalid_input", ["string", 123, (1, 2), None])
def test_quick_sort_type_error(invalid_input) -> None:
    with pytest.raises(TypeError):
        quick_sort(invalid_input)  # type: ignore


def test_quick_sort_uncomparable_elements() -> None:
    with pytest.raises(TypeError):
        quick_sort([1, "two", 3])


@pytest.mark.parametrize("size", [100, 1000, 5000])
def test_quick_sort_large_random_datasets(size: int) -> None:
    arr = [random.randint(-10000, 10000) for _ in range(size)]
    sorted_arr = quick_sort(arr.copy())
    assert sorted_arr == sorted(arr)