"""排序算法基准测试：时间/空间复杂度 & 十万级大规模数据验证"""
import time
import tracemalloc
import sys
from typing import Callable, Dict, Tuple
from src.sorting.algorithms import merge_sort, quick_sort, tim_sort

# 提升递归深度以支撑大规模快速排序
sys.setrecursionlimit(200000)

SORT_ALGORITHMS: Dict[str, Callable] = {
    "MergeSort": merge_sort,
    "QuickSort": quick_sort,
    "TimSort(Python内置)": tim_sort
}

SCALES = [10_000, 50_000, 100_000, 200_000]  # 包含十万级以上
DATA_TYPES = {
    "Random": lambda n: [x for x in __import__('random').sample(range(n*2), n)],
    "Sorted": lambda n: list(range(n)),
    "Reverse": lambda n: list(range(n, 0, -1)),
    "Duplicates": lambda n: [x % 10 for x in range(n)]
}

def run_benchmark(sort_func: Callable, arr: list) -> Tuple[float, float]:
    """执行单次基准测试，返回耗时(秒)与峰值内存(MB)"""
    tracemalloc.start()
    start = time.perf_counter()
    sort_func(arr.copy())  # 避免原地修改影响后续测试
    elapsed = time.perf_counter() - start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return elapsed, peak / (1024 * 1024)

def main():
    print("| 算法 | 数据规模 | 数据类型 | 耗时(s) | 峰值内存(MB) |")
    print("|------|----------|----------|---------|--------------|")
    
    for algo_name, func in SORT_ALGORITHMS.items():
        for scale in SCALES:
            for dtype, gen in DATA_TYPES.items():
                arr = gen(scale)
                t, m = run_benchmark(func, arr)
                print(f"| {algo_name} | {scale:>7,} | {dtype:<8} | {t:>7.4f} | {m:>12.2f} |")

if __name__ == "__main__":
    main()