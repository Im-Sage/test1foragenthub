from typing import List, Tuple

def knapsack_01(weights: List[int], values: List[int], capacity: int) -> int:
    """
    0/1 背包问题（空间优化版 DP）
    :param weights: 物品重量列表
    :param values: 物品价值列表
    :param capacity: 背包最大容量
    :return: 能装入的最大价值
    """
    if not weights or not values or capacity <= 0:
        return 0

    n = len(weights)
    dp = [0] * (capacity + 1)

    for i in range(n):
        w, v = weights[i], values[i]
        # 逆序遍历保证每个物品仅被选取一次
        for j in range(capacity, w - 1, -1):
            dp[j] = max(dp[j], dp[j - w] + v)

    return dp[capacity]


def knapsack_01_with_path(weights: List[int], values: List[int], capacity: int) -> Tuple[int, List[int]]:
    """
    0/1 背包问题（带回溯路径，返回最大价值及选中物品索引）
    :return: (最大价值, 选中物品索引列表)
    """
    if not weights or not values or capacity <= 0:
        return 0, []

    n = len(weights)
    # dp[i][j] 表示前 i 个物品在容量 j 下的最大价值
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        w, v = weights[i - 1], values[i - 1]
        for j in range(capacity + 1):
            if j >= w:
                dp[i][j] = max(dp[i - 1][j], dp[i - 1][j - w] + v)
            else:
                dp[i][j] = dp[i - 1][j]

    # 回溯找出具体选了哪些物品
    selected = []
    j = capacity
    for i in range(n, 0, -1):
        if dp[i][j] != dp[i - 1][j]:
            selected.append(i - 1)
            j -= weights[i - 1]

    return dp[n][capacity], selected[::-1]


if __name__ == "__main__":
    # 测试用例
    weights = [2, 3, 4, 5]
    values = [3, 4, 5, 6]
    capacity = 5

    max_val = knapsack_01(weights, values, capacity)
    print(f"最大价值: {max_val}")

    max_val_path, indices = knapsack_01_with_path(weights, values, capacity)
    print(f"最大价值: {max_val_path}, 选中物品索引: {indices}")