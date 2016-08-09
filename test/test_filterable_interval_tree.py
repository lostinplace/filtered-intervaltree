from intervaltree.i_tree_funcs import *
from intervaltree.bs_tree_funcs import inorder_walk
from .test_rb_tree import assert_black_balanced_trees, assert_relationships, assert_valid_rb_tree
from intervaltree.print_tree import print_tree_diagram
from .test_easy_hashes import id_generator
import random


def test_basic_filter_vector_generation():
    vector1 = generate_basic_filter_vector('test1')
    vector2 = generate_basic_filter_vector('test2')
    vector3 = generate_basic_filter_vector('test3')

    vector1plus2 = vector1 | vector2
    assert vector1 & vector1plus2 == vector1
    assert vector2 & vector1plus2 == vector2
    assert vector3 & vector1plus2 != vector3


def test_rb_insertion_integrity():
    test_tree = FilterableIntervalTree()
    random.seed('test')
    data = map(lambda _: (random.randint(0, 1000), random.randint(0, 20)), range(0, 100))
    print_tree_diagram(test_tree)
    for value in data:
        interval = Interval(value[0], value[0] + value[1])
        node = FilterableIntervalTreeNode(interval, {})
        add_node(test_tree, node)
        assert test_tree.root.black
        assert test_tree.nil.black
        assert_black_balanced_trees(test_tree)
        for node in inorder_walk(test_tree.root):
            assert node.black or not node.black
            if node.red:
                assert node.left_child.black and node.right_child.black


def generate_node(interval, filter_string):
    interval = Interval(*interval)
    vec = generate_basic_filter_vector(filter_string)
    node = FilterableIntervalTreeNode(interval, filter_string, vec)

    return node


def test_rotations():
    test_tree = FilterableIntervalTree()
    node_x = generate_node((5, 7), 'NODE X')
    node_y = generate_node((7, 9), 'NODE Y')
    node_alpha = generate_node((3, 6), 'NODE A')
    node_beta = generate_node((6, 12), 'NODE B')
    node_gamma = generate_node((8, 14), 'NODE G')

    coll = [node_x, node_y, node_alpha, node_beta, node_gamma]
    results = [add_node(test_tree, _) for _ in coll]
    right_rotated_relationships = [
        (test_tree.nil, node_x, "parent"),
        (node_y, node_x, "right_child"),
        (node_alpha, node_x, "left_child"),
        (node_beta, node_y, "left_child"),
        (node_gamma, node_y, "right_child")
    ]

    left_rotated_relationships = [
        (test_tree.nil, node_y, "parent"),
        (node_x, node_y, "left_child"),
        (node_alpha, node_x, "left_child"),
        (node_beta, node_x, "right_child"),
        (node_gamma, node_y, "right_child")
    ]

    vec = generate_basic_filter_vector

    assert_relationships(right_rotated_relationships)
    gqn = generate_query_node
    assert gqn(payload='NODE X') not in node_y
    assert gqn(payload='NODE G') in node_x
    assert gqn(payload='NODE Y') in node_x
    assert gqn(payload='NODE A') not in node_y

    # assert node_y.subtree_minimum == 6
    assert node_x.subtree_maximum == 14

    left_rotate(test_tree, node_x)
    assert_relationships(left_rotated_relationships)

    assert gqn(payload='NODE X') in node_y
    assert gqn(payload='NODE G') not in node_x
    assert gqn(payload='NODE Y') not in node_x
    assert gqn(payload='NODE A') in node_y

    # assert node_y.subtree_minimum == 3
    assert node_x.subtree_maximum == 12

    right_rotate(test_tree, node_y)
    assert_relationships(right_rotated_relationships)

    assert gqn(payload='NODE X') not in node_y
    assert gqn(payload='NODE G') in node_x
    assert gqn(payload='NODE Y') in node_x
    assert gqn(payload='NODE A') not in node_y

    # assert node_y.subtree_minimum == 6
    assert node_x.subtree_maximum == 14


def assert_valid_filterable_interval_tree(tree: FilterableIntervalTree):
    tracker_a = 0
    tracker_b = 0

    assert tree.nil.filter_vector == 0
    assert tree.nil.subtree_filter_vector == 0
    for node in inorder_walk(tree.root):
        tracker_a += 1
        qn = generate_query_node(payload=node.payload)

        vals = [node.key.end, node.left_child.subtree_maximum, node.right_child.subtree_maximum]
        assert node.subtree_maximum == max(vals)
        vecs = [node.filter_vector, node.left_child.subtree_filter_vector, node.right_child.subtree_filter_vector]
        minvec = 0
        for vec in vecs:
            minvec |= vec
        assert node.subtree_filter_vector == minvec
        parent = node.parent
        while parent:
            tracker_b += 1
            assert qn in parent
            assert node in parent
            # assert node.key.begin >= parent.subtree_minimum
            assert node.key.end <= parent.subtree_maximum
            parent = parent.parent


def test_fi_insertion_integrity():
    test_tree = FilterableIntervalTree()
    random.seed('test')
    data = map(lambda _: (random.randint(0, 1000), random.randint(0, 30)), range(0, 100))

    for value in data:
        interval = Interval(value[0], value[0] + value[1])
        payload = id_generator(15)
        node = FilterableIntervalTreeNode(interval, payload)
        add_node(test_tree, node)
        assert_valid_rb_tree(test_tree)
        assert_valid_filterable_interval_tree(test_tree)


def build_random_nodes(count):
    FITN = FilterableIntervalTreeNode
    data = map(lambda _: (random.randint(0, 1000), random.randint(0, 30)), range(0, count))
    intervals = map(lambda v: Interval(v[0], v[0] + v[1]), data)
    node_data = map(lambda i: FITN(i, id_generator(15)), intervals)
    nodes = list(node_data)
    return nodes


def insert_nodes(tree, nodes):
    for node in nodes:
        add_node(tree, node)


def test_search_interval_basic():
    fitn = FilterableIntervalTreeNode
    vec = generate_basic_filter_vector
    test_tree = FilterableIntervalTree()
    random.seed('test')
    interval_1_values = (75, 78)
    interval_1 = Interval(*interval_1_values)
    payload_1 = id_generator(15)
    node_1 = fitn(interval_1, payload_1)
    assert vec(payload_1) == node_1.filter_vector
    nodes = build_random_nodes(10000)
    insertion_index = random.randint(0, len(nodes)-1)
    nodes.insert(insertion_index, node_1)
    insert_nodes(test_tree, nodes)
    result_node = search_interval(test_tree, interval_1)
    assert result_node.key.overlaps(interval_1)


def test_search_interval_complete():
    test_tree = FilterableIntervalTree()
    random.seed('test')
    nodes = build_random_nodes(1000)
    insert_nodes(test_tree, nodes)
    random.shuffle(nodes)
    for node in nodes:
        result_node = search_interval(test_tree, node.key)
        assert result_node.key.overlaps(node.key)


def test_fi_removal_integrity():
    test_tree = FilterableIntervalTree()
    random.seed('test')

    # data = map(lambda _: random.weibullvariate(1, 1), range(0,100))

    nodes = build_random_nodes(500)
    insert_nodes(test_tree, nodes)

    random.shuffle(nodes)
    tracker = 0
    assert_valid_filterable_interval_tree(test_tree)
    for removal_node in nodes:
        delete_node(test_tree, removal_node)
        assert_valid_rb_tree(test_tree)
        assert_valid_filterable_interval_tree(test_tree)
        tracker += 1


def test_arbitrary_operations():
    test_tree = FilterableIntervalTree()
    random.seed('test')

    nodes = build_random_nodes(1000)
    insert_nodes(test_tree, nodes)

    random.shuffle(nodes)
    tracker = 0
    assert_valid_filterable_interval_tree(test_tree)
    ops = range(0, 100)
    for op in ops:
        choice = random.getrandbits(1)
        if choice:
            [node] = build_random_nodes(1)
            add_node(test_tree, node)
            insert_index = random.randint(0, len(nodes)-1)
            nodes.insert(insert_index, node)
        else:
            node = nodes.pop()
            delete_node(test_tree, node)

        assert_valid_rb_tree(test_tree)
        assert_valid_filterable_interval_tree(test_tree)
        interval_map = map(lambda x: x.key, nodes)
        for i in set(interval_map):
            result_node = search_interval(test_tree, i)
            assert result_node.key.overlaps(i)
        tracker += 1


def print_parents(tree, node):
    current = node
    tracker = 0
    while current is not tree.nil:
        print(current.payload, tracker)
        tracker += 1
        current = current.parent


def test_tree_query_basic():

    fitn = FilterableIntervalTreeNode
    vec = generate_basic_filter_vector
    test_tree = FilterableIntervalTree()
    random.seed('test')
    interval_1_values = (75, 78)
    interval_1 = Interval(*interval_1_values)
    payload_1 = id_generator(15)
    node_1 = fitn(interval_1, payload_1)
    assert vec(payload_1) == node_1.filter_vector
    nodes = build_random_nodes(10000)
    insertion_index = random.randint(0, len(nodes)-1)
    nodes.insert(insertion_index, node_1)
    insert_nodes(test_tree, nodes)

    query = generate_query_node(75, 78, payload_1)
    result_nodes = query_tree(test_tree, query, True)
    results = list(result_nodes)

    assert len(results) > 0

    for node in results:
        assert query.key in node.key
        assert query.payload == node.payload


def test_tree_10_records():

    fitn = FilterableIntervalTreeNode
    vec = generate_basic_filter_vector
    test_tree = FilterableIntervalTree()
    random.seed('test')
    nodes = build_random_nodes(10)
    insert_nodes(test_tree, nodes)

    random.shuffle(nodes)
    op_count = range(0, 10)
    for i in op_count:
        node = nodes[i]
        query = generate_query_node(node.key.begin, node.key.end, node.payload)
        results = query_tree(test_tree, query, True)
        result = next(results)

        assert result.payload == node.payload
        assert query.key in result.key


def test_adjust_payload():
    test_tree = FilterableIntervalTree()
    payload_a = {'name': 'chris'}
    node_a = FilterableIntervalTreeNode(Interval(50, 100), payload_a)
    add_node(test_tree, node_a)
    adjust_payload(test_tree, node_a, Interval(60, 70), {'state': 'b'})

    expectations = [
        (Interval(50, 60), payload_a),
        (Interval(60, 70), {'state': 'b', 'name': 'chris'}),
        (Interval(70, 100), payload_a)
    ]

    for i, node in enumerate(inorder_walk(test_tree.root)):
        assert node.key == expectations[i][0]
        assert node.payload == expectations[i][1]


def test_failed_consolidation():
    test_tree = FilterableIntervalTree()
    payload_a = {'name': 'chris'}
    node_a = FilterableIntervalTreeNode(Interval(50, 100), payload_a)
    add_node(test_tree, node_a)
    out = adjust_payload(test_tree, node_a, Interval(60, 70), {'name': 'manu'})
    adjust_payload(test_tree, out, Interval(65, 70), payload_a)

    expectations = [
        (Interval(50, 60), payload_a),
        (Interval(60, 65), {'name': 'manu'}),
        (Interval(65, 100), payload_a)
    ]

    a = list(inorder_walk(test_tree.root))
    assert len(a) == 3

#todo ensure that consolidation isn't consolidating nodes when there's a gap between them

# TODO Implement filter-aware predecesor and successor operations

#     0:3(a)
# -1:4(c)         3:5(a)
#          2:3(b)        6:6(a)
#                    5:18(c)
# get_predecessor for 3:5(a) == 0:3(a)
# get_successor for 3:5(a) == 5:6(a)


def test_get_predecessor_and_successor_for_node():
    test_tree = FilterableIntervalTree()
    payload_a = {'name': 'chris'}
    payload_b = {'name': 'manu'}
    payload_c = {'name': 'olly'}
    node_a = FilterableIntervalTreeNode(Interval(0, 3), payload_a)
    node_b = FilterableIntervalTreeNode(Interval(-1, 4), payload_c)
    node_c = FilterableIntervalTreeNode(Interval(3, 5), payload_a)
    node_d = FilterableIntervalTreeNode(Interval(2, 3), payload_b)
    node_e = FilterableIntervalTreeNode(Interval(6, 6), payload_a)
    node_f = FilterableIntervalTreeNode(Interval(5, 18), payload_c)
    add_node(test_tree, node_a)
    add_node(test_tree, node_b)
    add_node(test_tree, node_c)
    add_node(test_tree, node_d)
    add_node(test_tree, node_e)
    add_node(test_tree, node_f)

    result = get_predecessor_for_node(test_tree, node_c)
    assert result == node_a

    result = get_successor_for_node(test_tree, node_c)
    assert result == node_e


#           5:7(a)
#       3:5(c)       10:18(a)
#               6:7(a)       19:20(b)
#                    8:9(d)       21:23(a)
#                        9:10(a)

# get_maximum_node("5(a)", "b" ) == 9(b)
# get_maximum_node("3(c)", "b" ) == None

def test_get_maximum_for_node():
    tree = FilterableIntervalTree()
    payload_a = {'name': 'chris'}
    payload_b = {'name': 'manu'}
    payload_c = {'name': 'olly'}
    payload_d = {'name': 'lauren'}
    node_a = FilterableIntervalTreeNode(Interval(5, 7), payload_a)
    node_b = FilterableIntervalTreeNode(Interval(3, 5), payload_c)
    node_c = FilterableIntervalTreeNode(Interval(10, 18), payload_a)
    node_f = FilterableIntervalTreeNode(Interval(6, 7), payload_a)
    node_g = FilterableIntervalTreeNode(Interval(8, 9), payload_d)
    node_d = FilterableIntervalTreeNode(Interval(19, 20), payload_b)
    node_e = FilterableIntervalTreeNode(Interval(21, 23), payload_a)
    node_h = FilterableIntervalTreeNode(Interval(9, 10), payload_a)
    add_node(tree, node_a)
    add_node(tree, node_b)
    add_node(tree, node_c)
    add_node(tree, node_f)
    add_node(tree, node_g)
    add_node(tree, node_d)
    add_node(tree, node_e)
    add_node(tree, node_h)

    pot_max = get_maximum_node(tree, tree.root,  payload_b.__eq__)
    assert pot_max == node_d

    pot_max = get_maximum_node(tree, tree.root, payload_a.__eq__)
    assert pot_max == node_e

    ## because of rebalancing
    no_max = get_maximum_node(tree, node_c, payload_d.__eq__)
    assert no_max is None