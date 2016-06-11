from intervaltree.i_tree_funcs import *
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
        for node in RBTreeNode.inorder_walk(test_tree.root, False):
            assert node.black or not node.black
            if node.red:
                assert node.left_child.black and node.right_child.black



def generate_node(interval, filter_string):
    interval = Interval(*interval)
    node = FilterableIntervalTreeNode(interval, {})
    node.filter_vector = generate_basic_filter_vector(filter_string)
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

    assert vec('NODE X') not in node_y
    assert vec('NODE G') in node_x
    assert vec('NODE Y') in node_x
    assert vec('NODE A') not in node_y

    # assert node_y.subtree_minimum == 6
    assert node_x.subtree_maximum == 14

    left_rotate(test_tree, node_x)
    assert_relationships(left_rotated_relationships)

    assert vec('NODE X') in node_y
    assert vec('NODE G') not in node_x
    assert vec('NODE Y') not in node_x
    assert vec('NODE A') in node_y

    # assert node_y.subtree_minimum == 3
    assert node_x.subtree_maximum == 12

    right_rotate(test_tree, node_y)
    assert_relationships(right_rotated_relationships)

    assert vec('NODE X') not in node_y
    assert vec('NODE G') in node_x
    assert vec('NODE Y') in node_x
    assert vec('NODE A') not in node_y

    # assert node_y.subtree_minimum == 6
    assert node_x.subtree_maximum == 14


def assert_valid_filterable_interval_tree(tree: FilterableIntervalTree):
    for node in RBTreeNode.inorder_walk(tree.root):
        parent = node.parent
        while parent:
            assert generate_basic_filter_vector(node.payload) in parent
            assert node.filter_vector in parent
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
    nodes = build_random_nodes(100000)
    insertion_index = random.randint(0, len(nodes)-1)
    nodes.insert(insertion_index, node_1)
    insert_nodes(test_tree, nodes)
    result_node = search_interval(test_tree, interval_1)
    assert result_node.key.overlaps(interval_1)


def test_find_advanced():
    FITN = FilterableIntervalTreeNode
    vec = generate_basic_filter_vector
    test_tree = FilterableIntervalTree()
    random.seed('test')
    interval_1_values = (random.randint(0, 1000), random.randint(0, 30))
    interval_1 = Interval(*interval_1_values)
    payload_1 = id_generator(15)
    node_1 = FITN(interval_1, payload_1)
    assert vec(payload_1) == node_1.filter_vector
    data = map(lambda _: (random.randint(0, 1000), random.randint(0, 30)), range(0, 1000))
    intervals = map(lambda v: Interval(v[0], v[0]+v[1]), data)
    node_data = map(lambda i: FITN(i, id_generator(15)), intervals)
    nodes = list(node_data)
    insertion_index = random.randint(0, len(nodes)-1)
    nodes.insert(insertion_index, node_1)
    for node in nodes:
        add_node(test_tree, node)
    #TODO Test needs to be completed







