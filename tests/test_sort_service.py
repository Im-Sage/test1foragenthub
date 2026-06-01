import pytest
import random
import time
from typing import List
from services.sort_service import SortService

# 性能阈值配置（可根据CI环境调整）
LARGE_DATASET_SIZE = 50_000
PERFORMANCE_TIME_LIMIT = 2.0  # 秒

class TestSortService:
    """排序服务单元测试套件"""

    @staticmethod
    def _is_sorted(arr: List[int]) -> bool:
        return all(arr[i] <= arr[i + 1] for i in range(len(arr) - 1))

    @pytest.fixture
    def service(self):
        return SortService()

    def test_random_array_correctness(self, service):
        """常规随机数组：验证排序正确性"""
        size = 1000
        arr = [random.randint(-1000, 1000) for _ in range(size)]
        result = service.sort_array(arr)
        
        assert self._is_sorted(result)
        assert result == sorted(arr)

    def test_already_sorted(self, service):
        """已排序数组：验证稳定性与基础性能"""
        arr = list(range(1, 1001))
        start = time.perf_counter()
        result = service.sort_array(arr)
        elapsed = time.perf_counter() - start
        
        assert result == arr
        assert self._is_sorted(result)
        assert elapsed < 0.5, f"已排序数组处理超时: {elapsed:.3f}s"

    def test_reverse_sorted(self, service):
        """逆序数组：验证算法对最坏情况的处理能力"""
        arr = list(range(1000, 0, -1))
        start = time.perf_counter()
        result = service.sort_array(arr)
        elapsed = time.perf_counter() - start
        
        assert result == list(range(1, 1001))
        assert self._is_sorted(result)
        assert elapsed < 1.0, f"逆序数组处理超时: {elapsed:.3f}s"

    def test_heavy_duplicates(self, service):
        """大量重复元素：验证边界比较与稳定性"""
        arr = [random.choice([1, 2, 3, 5]) for _ in range(2000)]
        result = service.sort_array(arr)
        
        assert self._is_sorted(result)
        assert result == sorted(arr)
        # 验证元素数量未丢失
        from collections import Counter
        assert Counter(arr) == Counter(result)

    @pytest.mark.parametrize("size", [1, 500, 10_000])
    def test_edge_cases_and_scalability(self, service, size):
        """边界值与规模扩展测试"""
        if size == 1:
            arr = [42]
        else:
            arr = [random.randint(-size, size) for _ in range(size)]
            
        result = service.sort_array(arr)
        assert self._is_sorted(result)
        assert len(result) == len(arr)

    def test_performance_large_dataset(self, service):
        """大数据集性能压测：验证 O(n log n) 实际耗时"""
        arr = [random.randint(-100_000, 100_000) for _ in range(LARGE_DATASET_SIZE)]
        
        start = time.perf_counter()
        result = service.sort_array(arr)
        elapsed = time.perf_counter() - start
        
        assert self._is_sorted(result)
        assert elapsed < PERFORMANCE_TIME_LIMIT, (
            f"大数据集排序性能不达标: {elapsed:.3f}s > {PERFORMANCE_TIME_LIMIT}s"
        )