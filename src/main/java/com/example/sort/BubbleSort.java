package com.example.sort;

import java.util.Comparator;

/**
 * 冒泡排序实现（优化版）
 * <ul>
 *   <li>最好时间复杂度：O(n)（已排序）</li>
 *   <li>平均/最坏时间复杂度：O(n²)</li>
 *   <li>空间复杂度：O(1)（原地排序）</li>
 *   <li>稳定性：✅ 稳定</li>
 * </ul>
 */
public final class BubbleSort {

    private BubbleSort() {
        throw new UnsupportedOperationException("Utility class");
    }

    /**
     * 对数组进行升序冒泡排序
     * @param arr 待排序数组，若为 null 或长度小于2则直接返回
     * @throws IllegalArgumentException 如果数组元素为 null
     */
    public static void sort(int[] arr) {
        if (arr == null || arr.length < 2) {
            return;
        }
        int n = arr.length;
        int lastSwapIndex = n - 1;

        while (lastSwapIndex > 0) {
            int newSwapIndex = 0;
            for (int j = 0; j < lastSwapIndex; j++) {
                if (arr[j] > arr[j + 1]) {
                    swap(arr, j, j + 1);
                    newSwapIndex = j;
                }
            }
            lastSwapIndex = newSwapIndex; // 已排序后缀不再参与比较
        }
    }

    /**
     * 泛型冒泡排序（支持自定义比较器）
     */
    public static <T> void sort(T[] arr, Comparator<T> comparator) {
        if (arr == null || comparator == null || arr.length < 2) {
            return;
        }
        int n = arr.length;
        int lastSwapIndex = n - 1;

        while (lastSwapIndex > 0) {
            int newSwapIndex = 0;
            for (int j = 0; j < lastSwapIndex; j++) {
                if (comparator.compare(arr[j], arr[j + 1]) > 0) {
                    T tmp = arr[j];
                    arr[j] = arr[j + 1];
                    arr[j + 1] = tmp;
                    newSwapIndex = j;
                }
            }
            lastSwapIndex = newSwapIndex;
        }
    }

    private static void swap(int[] arr, int i, int j) {
        int tmp = arr[i];
        arr[i] = arr[j];
        arr[j] = tmp;
    }
}