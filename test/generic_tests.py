import random
from intervaltree.bs_tree_node import BSTreeNode
import timeit


def test_compare_addition():
    random.seed('test')

    data = map(lambda _: random.randint(0, 1000), range(0, 10000))
    node_map = map(BSTreeNode, data)
    node_list = list(node_map)

    p = "key"

    b = True
    g_op_1 = lambda: [getattr(interval, "key" if b else "left_child") for interval in node_list]
    g_op_2 = lambda: [_.key if b else _.left_child for _ in node_list]

    s_op_1 = lambda: [setattr(interval, "key", val) for interval in node_list]

    val = 0

    def set(node):
        if b:
            node.key = val
        else:
            node.key = val

    s_op_2 = lambda: [set(_) for _ in node_list]

    repetitions = 200

    g_op_1_result = timeit.timeit(g_op_1, number=repetitions)
    g_op_2_result = timeit.timeit(g_op_2, number=repetitions)
    s_op_1_result = timeit.timeit(s_op_1, number=repetitions)
    s_op_2_result = timeit.timeit(s_op_2, number=repetitions)

    assert g_op_1_result < g_op_2_result
    assert s_op_1_result < s_op_2_result


def test_some_nonsense():

    class stub():
        def __init__(self, string):
            self.tstr = string

        def blah(self, string):
            return self.tstr == string

    s = stub('ok')

    class testclass():
        def __init__(self, an_int):
            self.teq = an_int.__eq__
            self.tblah = s.blah

    t = testclass(5)
    assert t.teq(5)
    assert not t.teq(6)
    assert t.tblah('ok')
    assert not t.tblah('not ok')

