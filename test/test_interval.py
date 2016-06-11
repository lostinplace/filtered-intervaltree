from intervaltree.interval import *


def test_basic():
    t = Interval(1, 2)
    assert t.begin is 1
    assert t.end is 2


def test_removal_no_overlap():
    interval_one = Interval(10, 15)
    interval_two = Interval(8, 10)
    result = interval_one.remove(interval_two)
    assert result == [interval_one]


def test_removal_whole_contains():
    interval_one = Interval(10, 20)
    interval_two = Interval(12, 17)
    expectation = [
        Interval(10, 12),
        Interval(17, 20)
    ]
    result = interval_one.remove(interval_two)
    assert result == expectation


def test_removal_reduction():
    interval_one = Interval(10, 20)
    interval_two = Interval(10, 12)
    expectation = [
        Interval(12, 20)
    ]
    result = interval_one.remove(interval_two)
    assert result == expectation

    interval_one = Interval(10, 20)
    interval_two = Interval(18, 20)
    expectation = [
        Interval(10, 18)
    ]
    result = interval_one.remove(interval_two)
    assert result == expectation


def test_removal_overlap():
    interval_one = Interval(10, 20)
    interval_two = Interval(8, 12)
    expectation = [
        Interval(12, 20)
    ]
    result = interval_one.remove(interval_two)
    assert result == expectation

    interval_one = Interval(10, 20)
    interval_two = Interval(18, 24)
    expectation = [
        Interval(10, 18)
    ]
    result = interval_one.remove(interval_two)
    assert result == expectation

def test_removal_edge_cases():
    interval_one = Interval(10, 20)
    interval_two = Interval(10, 10)
    expectation = [
        Interval(10, 20)
    ]
    result = interval_one.remove(interval_two)
    assert result == expectation

    interval_one = Interval(10, 20)
    interval_two = Interval(20, 20)
    expectation = [
        Interval(10, 20)
    ]
    result = interval_one.remove(interval_two)
    assert result == expectation

    interval_one = Interval(10, 10)
    interval_two = Interval(10, 20)
    expectation = [
    ]
    result = interval_one.remove(interval_two)
    assert result == expectation

    interval_one = Interval(10, 15)
    interval_two = Interval(8, 20)
    expectation = [
    ]
    result = interval_one.remove(interval_two)
    assert result == expectation


import timeit
import random


def test_compare_addition():
    num_ops = 10000
    op_range = range(0, num_ops)
    random.seed('test')

    data = map(lambda _: (random.randint(0, 1000), random.randint(0, 30)), range(0, 1000))
    intervals = map(lambda v: Interval(v[0], v[0] + v[1]), data)
    interval_list = list(intervals)
    pairs_map = map(lambda _:(random.choice(interval_list), random.choice(interval_list)), op_range)
    pairs = list(pairs_map)
    trips_map = map(lambda _:(random.choice(interval_list), random.choice(interval_list), random.choice(interval_list)),
                    op_range)
    trips = list(trips_map)

    op_1 = lambda: [combine_intervals(pair[0], pair[1]) for pair in pairs]
    op_2 = lambda: [get_minimum_bounding_interval(pair[0], pair[1]) for pair in pairs]
    op_3 = lambda: [pair[0] + pair[1] for pair in pairs]

    op_3x_1 = lambda: [combine_intervals(combine_intervals(trip[0], trip[1]), trip[2]) for trip in trips]
    op_3x_2 = lambda: [combine_three_intervals(trip[0], trip[1], trip[2]) for trip in trips]

    repetitions = 20

    op_1_result = timeit.timeit(op_1, number=repetitions)
    op_2_result = timeit.timeit(op_2, number=repetitions)
    op_3_result = timeit.timeit(op_3, number=repetitions)
    op_3x_1_result = timeit.timeit(op_3x_1, number=repetitions)
    op_3x_2_result = timeit.timeit(op_3x_2, number=repetitions)

    assert op_3x_2_result < op_3x_1_result
    assert op_1_result < op_2_result
    assert op_3_result > op_1_result
    # assert op_3_result < op_2_result


