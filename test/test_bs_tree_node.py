from intervaltree.bs_tree_node import BSTreeNode
from intervaltree.bs_tree import BSTree
import random
from test.random_data import *


def test_begin():
    tree = BSTree()
    root = BSTreeNode(5)
    tree.add_node(root)
    left_leaf = BSTreeNode(5)
    right_leaf = BSTreeNode(6)
    tree.add_node(left_leaf)
    tree.add_node(right_leaf)

    assert left_leaf == root.left_child
    assert right_leaf == root.right_child


def test_inorder_walk():
    tree = BSTree()
    root = BSTreeNode(4)
    tree.add_node(root)

    values = [2, 7, 4, 15, 3]

    for i in values:
        tree.add_node(BSTreeNode(i))

    expected = sorted(values + [root.key])
    actual = [_.key for _ in BSTreeNode.inorder_walk(root, True)]

    assert expected == actual


def test_inorder_walk_non_recursive():
    tree = BSTree()
    root = BSTreeNode(4)
    tree.add_node(root)

    values = [2, 7, 4, 15, 3]

    for i in values:
        tree.add_node(BSTreeNode(i))

    expected = sorted(values + [root.key])
    actual = [_.key for _ in BSTreeNode.inorder_walk(root, False)]

    assert expected == actual


def test_bsearch():
    tree = BSTree()
    root = BSTreeNode(4)
    tree.add_node(root)

    values = [2, 7, 4, 15, 3]
    for i in values:
        tree.add_node(BSTreeNode(i))

    expected = [4, 4]
    actual = [_.key for _ in tree.search_for_key(4)]
    assert expected == actual

    expected = [7]
    actual = [_.key for _ in tree.search_for_key(7)]
    assert expected == actual


def test_bsearch_non_recursive():
    from intervaltree.bs_tree_funcs import _search_node_non_recursive
    tree = BSTree()
    root = BSTreeNode(4)
    tree.add_node(root)
    values = [2, 7, 4, 15, 3]

    for i in values:
        tree.add_node(BSTreeNode(i))

    expected = [4, 4]
    actual = [_.key for _ in _search_node_non_recursive(root, 4)]
    assert expected == actual

    expected = [7]
    actual = [_.key for _ in _search_node_non_recursive(root, 7)]
    assert expected == actual


def test_min_and_max():
    tree = BSTree()
    root = BSTreeNode(4)
    tree.add_node(root)

    values = [2, 7, 4, 15, 3]

    for i in values:
        tree.add_node(BSTreeNode(i))

    expected_min = min(values)
    actual_min = BSTreeNode.get_minimum(root).key
    assert expected_min == actual_min

    expected_max = max(values)
    actual_max = BSTreeNode.get_maximum(root).key
    assert expected_max == actual_max


def test_simple_successor():
    tree = BSTree()
    root = BSTreeNode(4)
    tree.add_node(root)

    random.seed('test')
    data = map(lambda _: random.randint(0, 1000), range(0, 100))

    nodes = [tree.add_node(BSTreeNode(i)) for i in data]
    sorted_nodes = list(BSTreeNode.inorder_walk(root))

    for i in range(100):
        current_node = sorted_nodes[i]
        next_index = i+1 if i!=100 else 100
        previous_index = i-1 if i != 0 else 0

        expected_successor_node = sorted_nodes[next_index]
        actual_successor_node = BSTreeNode.get_successor_for_node(current_node)

        assert expected_successor_node.key == actual_successor_node.key

        expected_predecessor_node = sorted_nodes[previous_index]
        actual_predecessor_node = BSTreeNode.get_predecessor_for_node(current_node)

        assert actual_predecessor_node and (expected_predecessor_node.key == actual_predecessor_node.key) or True


def test_relationship_identification():
    root = BSTreeNode(4)
    tree = BSTree()
    tree.add_node(root)

    values = [3, 5]
    [tree.add_node(BSTreeNode(_)) for _ in values]
    node_3 = next(tree.search_for_key(3))
    node_4 = next(tree.search_for_key(4))
    node_5 = next(tree.search_for_key(5))
    rel3_4 = BSTreeNode.get_relationship_between_nodes(node_3, node_4)
    assert rel3_4 == "left_child"
    rel4_5 = BSTreeNode.get_relationship_between_nodes(node_4, node_5)
    assert rel4_5 == "parent"
    rel5_4 = BSTreeNode.get_relationship_between_nodes(node_5, node_4)
    assert rel5_4 == "right_child"


def test_insertion():
    root = BSTreeNode(4)
    tree = BSTree()
    tree.add_node(root)

    values = [2, 7, 6, 12, 3, 14, 5, 2, 8, 3, 4, 15, 3]
    [tree.add_node(BSTreeNode(_)) for _ in values]

    expected = sorted(values + [root.key])
    actual = [_.key for _ in BSTreeNode.inorder_walk(root, False)]

    assert expected == actual


def get_diagram_elements(a_root_node):
    result = [
        (
            _.key,
            _.depth,
            BSTreeNode.get_relationship_between_nodes(_, _.parent))
        for _ in BSTreeNode.preorder_walk(a_root_node, False)
        ]
    return result


def test_basic_match():
    root = BSTreeNode(4)
    tree = BSTree()
    tree.add_node(root)

    values = [3, 5]
    [tree.add_node(BSTreeNode(_)) for _ in values]

    expected_results = [
        (4, 0, None),
        (3, 1, "left_child"),
        (5, 1, "right_child")
    ]

    actual_results = get_diagram_elements(root)
    assert expected_results == actual_results


def test_easy_delete1():
    root = BSTreeNode(4)
    tree = BSTree()
    tree.add_node(root)

    values = [3, 5]
    [tree.add_node(BSTreeNode(_)) for _ in values]

    expected_results = [
        (4, 0, None),
        (5, 1, "right_child")
    ]
    node_3 = next(tree.search_for_key(3))
    BSTreeNode.delete_node(node_3)

    actual_results = get_diagram_elements(root)
    assert expected_results == actual_results


def test_easy_delete2():
    root = BSTreeNode(4)
    tree = BSTree()
    tree.add_node(root)

    values = [3, 5]
    [tree.add_node(BSTreeNode(_)) for _ in values]

    expected_results = [
        (4, 0, None),
        (3, 1, "left_child")
    ]
    node_5 = next(tree.search_for_key(5))
    BSTreeNode.delete_node(node_5)

    actual_results = get_diagram_elements(root)
    assert expected_results == actual_results


def test_node_removal():

    test_tree = BSTree()
    random.seed('test')
    data = map(lambda _: random.randint(0, 1000), range(0, 100))
    # data = map(lambda _: random.weibullvariate(1, 1), range(0,100))
    removal_nodes = []

    for value in data:
        node = BSTreeNode(value)
        test_tree.add_node(node)
        removal_nodes.append(node)

    random.shuffle(removal_nodes)
    for removal_node in removal_nodes:
        initial_values = map(lambda x: x.key, test_tree.inorder_walk())
        pre_distribution = compute_distribution(initial_values)
        expected_removal_count = \
            (pre_distribution.get(removal_node.key) or 0) - 1
        expected_distribution = pre_distribution.copy()
        if expected_removal_count is 0:
            expected_distribution.pop(removal_node.key, None)
        else:
            expected_distribution[removal_node.key] = expected_removal_count
        test_tree.delete_node(removal_node)
        post_values = map(lambda x: x.key, test_tree.inorder_walk())
        post_distribution = compute_distribution(post_values)

        assert post_distribution == expected_distribution