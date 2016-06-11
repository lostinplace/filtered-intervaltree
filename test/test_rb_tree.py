import random
from intervaltree.print_tree import *
from intervaltree.rb_tree import *
from intervaltree.rb_tree_node import *
from collections import deque


def test_begin():
    test_tree = RBTree()
    assert test_tree.root is None

    assert isinstance(test_tree.nil, RBTreeNode)
    assert test_tree.nil.key is None
    assert test_tree.nil.black


def test_tree_addition():
    test_tree = RBTree()
    assert test_tree.root is None
    node_x = RBTreeNode(5)
    test_tree.add_node(node_x)
    assert test_tree.root is node_x
    assert node_x.left_child is test_tree.nil
    assert node_x.right_child is test_tree.nil


def assert_relationships(relationships):
    for i in relationships:
        assert BSTreeNode.get_relationship_between_nodes(i[0], i[1]) is i[2]


def test_left_rotate():
    test_tree = RBTree()

    node_x = RBTreeNode(5)
    node_y = RBTreeNode(7)
    node_alpha = RBTreeNode(3)
    node_beta = RBTreeNode(6)
    node_gamma = RBTreeNode(8)
    coll = [node_x, node_y, node_alpha, node_beta, node_gamma]
    results = [test_tree.add_node(_) for _ in coll]
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
    assert_relationships(right_rotated_relationships)
    RBTreeNode.left_rotate(test_tree, node_x)
    assert_relationships(left_rotated_relationships)


def test_right_rotate():
    test_tree = RBTree()

    node_x = RBTreeNode(5)
    node_y = RBTreeNode(7)
    node_alpha = RBTreeNode(3)
    node_beta = RBTreeNode(6)
    node_gamma = RBTreeNode(8)
    coll = [node_x, node_y, node_alpha, node_beta, node_gamma]
    results = [test_tree.add_node(_) for _ in coll]
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

    assert_relationships(right_rotated_relationships)
    RBTreeNode.left_rotate(test_tree, node_x)
    assert_relationships(left_rotated_relationships)
    RBTreeNode.right_rotate(test_tree, node_y)
    assert_relationships(right_rotated_relationships)


def test_rb_insertion_integrity():
    test_tree = RBTree()
    random.seed('test')
    data = map(lambda _: random.randint(0, 1000), range(0,100))

    for value in data:
        node = RBTreeNode(value)
        test_tree.add_node(node)
        assert_valid_rb_tree(test_tree)


def assert_valid_rb_tree(a_tree: RBTree):
    assert a_tree.root.black
    assert a_tree.nil.black
    assert_black_balanced_trees(a_tree)
    for node in RBTreeNode.inorder_walk(a_tree.root, False):
        assert node.black or not node.black
        if node.red:
            assert node.left_child.black and node.right_child.black


def assert_black_balanced_trees(a_tree: RBTree):
    results = {
        a_tree.nil: 0,
        None: 0
    }

    queue = deque([a_tree.root])

    while queue:
        current = queue.popleft()
        left_val = results.get(current.left_child)
        right_val = results.get(current.right_child)

        if left_val is None or right_val is None:
            queue.appendleft(current)
            if right_val is None:
                queue.appendleft(current.right_child)
            if left_val is None:
                queue.appendleft(current.left_child)
        else:
            assert left_val == right_val
            results[current] = left_val + (1 if current.black else 0)


def test_rb_removal_integrity():
    test_tree = RBTree()
    random.seed('test')
    data = map(lambda _: random.randint(0, 1000), range(0,100))
    # data = map(lambda _: random.weibullvariate(1, 1), range(0,100))
    removal_nodes = []

    for value in data:
        node = RBTreeNode(value)
        test_tree.add_node(node)
        removal_nodes.append(node)

    random.shuffle(removal_nodes)
    for removal_node in removal_nodes:
        RBTree.delete_node(test_tree, removal_node)
        assert_valid_rb_tree(test_tree)



def test_rb_transplant():
    test_tree = RBTree()

    node_x = RBTreeNode(5)
    node_y = RBTreeNode(7)
    node_alpha = RBTreeNode(3)
    node_beta = RBTreeNode(6)
    node_gamma = RBTreeNode(8)
    coll = [node_x, node_y, node_alpha, node_beta, node_gamma]
    results = [test_tree.add_node(_) for _ in coll]
    node_delta = RBTreeNode('test')
    RBTree.transplant(test_tree, node_y, node_delta)
    assert node_delta.parent is node_x
    assert node_x.right_child is node_delta





