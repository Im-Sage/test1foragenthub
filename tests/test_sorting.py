"""排序算法自动化单元测试：覆盖正确性 & 稳定性"""
import pytest
from src.sorting.algorithms import merge_sort, quick_sort, tim_sort

# 测试数据生成器
DATA_GENERATORS = {
    "random": lambda n: [i % 100 for i in range(n)],  # 常规随机
    "sorted": lambda n: list(range(n)),               # 已排序
    "reverse": lambda n: list(range(n, 0, -1)),       # 逆序
    "duplicates": lambda n: [i % 5 for i in range(n)] # 大量重复
}

SORT_FUNCS = {
    "merge_sort": merge_sort,
    "quick_sort": quick_sort,
    "tim_sort": tim_sort
}

@pytest.mark.parametrize("algo_name, sort_func", SORT_FUNCS.items())
@pytest.mark.parametrize("data_name, gen", DATA_GENERATORS.items())
class TestSortingCorrectness:
    """验证各场景下的排序正确性"""
    def test_correctness(self, algo_name, sort_func, data_name, gen):
        size = 100  # 单元测试用小规模
        arr = gen(size)
        expected = sorted(arr)
        assert sort_func(arr) == expected, f"{algo_name} 在 {data_name} 数据下排序结果错误"

@pytest.mark.parametrize("algo_name, sort_func", SORT_FUNCS.items())
class TestSortingStability:
    """验证算法稳定性：相同值的原始相对顺序是否保持不变"""
    def test_stability(self, algo_name, sort_func):
        # 构造 (值, 原始索引) 元组列表
        arr = [(3, 0), (1, 1), (3, 2), (2, 3), (1, 4), (3, 5)]
        result = sort_func(arr)
        # 提取值相等的子序列，验证索引是否严格递增
        values = [x[0] for x in result]
        indices = [x[1] for x in result]
        
        # 稳定性断言：对任意相同值，其在结果中的索引顺序应与原数组一致
        from collections import defaultdict
        pos_map = defaultdict(list)
        for val, idx in zip(values, indices):
            pos_map[val].append(idx)
            
        for val, idx_list in pos_map.items():
            assert idx_list == sorted(idx_list), f"{algo_name} 不稳定：值 {val} 的相对顺序被打乱"