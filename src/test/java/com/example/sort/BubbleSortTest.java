package com.example.sort;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.MethodSource;

import java.util.Arrays;
import java.util.Comparator;
import java.util.stream.Stream;

import static org.junit.jupiter.api.Assertions.*;

class BubbleSortTest {

    @Test
    void shouldHandleNullAndSmallArrays() {
        assertDoesNotThrow(() -> BubbleSort.sort(null));
        assertDoesNotThrow(() -> BubbleSort.sort(new int[]{}));
        assertDoesNotThrow(() -> BubbleSort.sort(new int[]{5}));
        assertEquals(5, new int[]{5}[0]);
    }

    @Test
    void shouldSortAlreadySortedArray() {
        int[] arr = {1, 2, 3, 4, 5};
        int[] expected = arr.clone();
        BubbleSort.sort(arr);
        assertArrayEquals(expected, arr);
    }

    @Test
    void shouldSortReverseArray() {
        int[] arr = {5, 4, 3, 2, 1};
        int[] expected = {1, 2, 3, 4, 5};
        BubbleSort.sort(arr);
        assertArrayEquals(expected, arr);
    }

    @Test
    void shouldHandleDuplicates() {
        int[] arr = {3, 1, 2, 3, 2, 1};
        int[] expected = {1, 1, 2, 2, 3, 3};
        BubbleSort.sort(arr);
        assertArrayEquals(expected, arr);
    }

    @ParameterizedTest(name = "Sort {0}")
    @MethodSource("provideRandomArrays")
    void shouldSortRandomArrays(int[] arr) {
        int[] expected = arr.clone();
        Arrays.sort(expected);
        BubbleSort.sort(arr);
        assertArrayEquals(expected, arr, "排序结果与标准库不一致");
    }

    static Stream<int[]> provideRandomArrays() {
        return Stream.of(
                new int[]{9, -1, 0, 100, -50},
                new int[]{Integer.MAX_VALUE, Integer.MIN_VALUE, 0},
                new int[]{1, 1, 1, 1},
                new int[]{10, 9, 8, 7, 6, 5, 4, 3, 2, 1}
        );
    }

    @Test
    void shouldPreserveStability() {
        // 验证稳定性：相等元素的原始相对顺序不变
        Record[] arr = {
                new Record(2, "A"), new Record(1, "B"),
                new Record(2, "C"), new Record(1, "D")
        };
        BubbleSort.sort(arr, Comparator.comparingInt(Record::value));

        // 期望：值相同的元素保持原出现顺序
        assertEquals("B", arr[0].label);
        assertEquals("D", arr[1].label);
        assertEquals("A", arr[2].label);
        assertEquals("C", arr[3].label);
    }

    record Record(int value, String label) {}
}