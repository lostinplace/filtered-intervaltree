from intervaltree.interval import Interval
from .rb_tree import RBTree
from .rb_tree import RBTreeNode
from .rb_tree_funcs import redblack_insert_fixup, left_rotate as rb_lr, right_rotate as rb_rr, \
    rb_delete_fixup as rb_df, delete_node as rb_d, tree_successor
from .easy_hashes import hash_to_64
import collections
import sys
import math


def check_contains(node: 'FilterableIntervalTreeNode', content):
    """
    checks to see if the specified content is available in the node's subtrees
    :param node: node root to search
    :param content: content to search for, cand be a filterablenode, a filter vector, or content that generates a filter vector
    :return: true if available
    """
    if isinstance(content, int):
        vector = content
    elif isinstance(content, FilterableIntervalTreeNode):
        vector = content.filter_vector
    elif hasattr(content, 'generate_filter_vector'):
        vector = content.generate_filter_vector
    else:
        vector = generate_basic_filter_vector(str(content))
    return (vector & node.subtree_filter_vector) == content


class FilterableIntervalTreeNode(RBTreeNode):

    def __init__(self, key: Interval, payload=None, filter_vector: int=0):
        self.key = key,
        self.payload = payload or None
        if key is not None:
            self.subtree_maximum = key.end

        if not filter_vector:
            if hasattr(payload, 'generate_filter_vector'):
                self.filter_vector = payload.generate_filter_vector
            else:
                self.filter_vector = generate_basic_filter_vector(str(payload))
        else:
            self.filter_vector = filter_vector
        self.subtree_filter_vector = self.filter_vector
        super().__init__(key)

    def __contains__(self, item):
        return check_contains(self, item)


class FilterableIntervalTree(RBTree):

    def __init__(self):
        super().__init__()
        self.nil = FilterableIntervalTreeNode(None, None)
        self.nil.black = True
        self.nil.tree = self
        self.nil.subtree_maximum = -math.inf


def generate_basic_filter_vector(value: str):
    bit_indexes = hash_to_64(value, 5)
    result = 0
    for i in bit_indexes:
        result |= 1 << i
    return result


def update_subtree_filter_vector(node: FilterableIntervalTreeNode):
    a = node.left_child
    b = node.right_child
    node.subtree_filter_vector = a.subtree_filter_vector | b.subtree_filter_vector | node.filter_vector


def update_subtree_max_after_rotate(node: FilterableIntervalTreeNode):
    pm = node.parent.subtree_maximum
    p_less = pm < node.subtree_maximum
    if p_less:
        node.parent.subtree_maximum = node.subtree_maximum
    else:
        gsm = node.left_child.subtree_maximum
        asm = node.right_child.subtree_maximum
        node.subtree_maximum = max(
            node.key.end,
            gsm,
            asm
        )


def left_rotate(tree: FilterableIntervalTree, node: FilterableIntervalTreeNode):
    result = rb_lr(tree, node)
    update_subtree_filter_vector(node)
    update_subtree_filter_vector(node.parent)
    update_subtree_max_after_rotate(node)
    return node


def right_rotate(tree: FilterableIntervalTree, node: FilterableIntervalTreeNode):
    result = rb_rr(tree, node)
    update_subtree_filter_vector(node)
    update_subtree_filter_vector(node.parent)
    update_subtree_max_after_rotate(node)
    return node


def add_node(tree: FilterableIntervalTree, node: FilterableIntervalTreeNode) -> FilterableIntervalTreeNode:
    node.tree = tree
    node.left_child = node.right_child = tree.nil
    end = node.key.end
    begin = node.key.begin
    if tree.root is None:
        tree.root = node
        node.parent = tree.nil
        node.black = True
        return node

    current_node = tree.root
    while current_node is not tree.nil:
        last_parent = current_node
        going_left = begin <= current_node.key.begin
        if end > current_node.subtree_maximum:
            current_node.subtree_maximum = end
        current_node.subtree_filter_vector |= node.filter_vector
        current_node = last_parent.left_child if going_left else last_parent.right_child

    if going_left:
        last_parent.left_child = node
    else:
        last_parent.right_child = node
    node.parent = last_parent
    redblack_insert_fixup(tree, node, left_rotate_func=left_rotate, right_rotate_func=right_rotate)


def transplant(tree, a_node: FilterableIntervalTreeNode, a_replacement: FilterableIntervalTreeNode):
    u = a_node
    u_parent = u.parent
    v = a_replacement
    if u.subtree_maximum == u.key.end:
        v.subtree_maximum = max(u.left_child.subtree_maximum, u.right_child.subtree_maximum, v.subtree_maximum)
    else:
        v.subtree_maximum = max(u.subtree_maximum, v.subtree_maximum)
    if u is tree.root:
        tree.root = v
    elif u is u_parent.left_child:
        u_parent.left_child = v
    else:
        u_parent.right_child = v
    v.parent = u_parent
    if u_parent is not tree.nil:
        update_subtree_filter_vector(u_parent)


def update_statistics_in_chain(tree: FilterableIntervalTree, node: FilterableIntervalTreeNode):
    parent = node.parent
    while parent is not tree.nil:
        parent.subtree_maximum = max(
            parent.key.end,
            parent.left_child.subtree_maximum,
            parent.right_child.subtree_maximum
        )
        parent = parent.parent


def delete_node(tree: FilterableIntervalTree, node: FilterableIntervalTreeNode):
    z = node
    y = z
    y_original_color = y.color

    if z.left_child is tree.nil:
        x = z.right_child
        transplant(tree, z, z.right_child)
    elif z.right_child is tree.nil:
        x = z.left_child
        transplant(tree, z, z.left_child)
    else:
        y = tree_successor(tree, z)
        y_original_color = y.color
        x = y.right_child
        if y.parent is z:
            x.parent = y
        else:
            transplant(tree, y, y.right_child)
            y.right_child = z.right_child
            y.right_child.parent = y
            y.subtree_filter_vector = z.right_child.subtree_filter_vector | y.filter_vector

        y.left_child = z.left_child
        y.left_child.parent = y
        y.subtree_filter_vector |= z.left_child.subtree_filter_vector
        transplant(tree, z, y)
        y.color = z.color
    if y_original_color is "black":
        rb_df(tree, x, left_rotate, right_rotate)
    update_statistics_in_chain(tree, x)
    tree.nil.parent = None



def search_interval(tree: FilterableIntervalTree, interval: Interval) -> FilterableIntervalTreeNode:
    x = tree.root
    while x and not interval.overlaps(x.key):
        if x.left_child and x.left_child.subtree_maximum > interval.begin:
            x = x.left_child
        else:
            x = x.right_child
    return x

