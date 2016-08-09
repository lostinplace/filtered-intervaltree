from intervaltree.interval import Interval, interval_overlaps, interval_contains
from .rb_tree import RBTree
from .rb_tree import RBTreeNode
from .rb_tree_funcs import redblack_insert_fixup, left_rotate as rb_lr, right_rotate as rb_rr, \
    rb_delete_fixup as rb_df, tree_successor
from .easy_hashes import hash_to_64
import math
from typing import Generator, Callable, List, Any
import numbers
from collections import deque


def check_contains(node: 'FilterableIntervalTreeNode', content: 'FilterableIntervalTreeNode'):
    """
    checks to see if the specified content is available in the node's subtrees
    :param node: node root to search
    :param content: content to search for, cand be a filterablenode, a filter vector, or content that generates a
        filter vector
    :return: true if available
    """
    is_contained = content.filter_vector & node.subtree_filter_vector == content.filter_vector

    return is_contained


def generate_query_node(begin: int=-math.inf, end: int=math.inf, payload=None, filter_vector: int=None):
    tmp_interval = Interval(begin, end)
    vector = None
    if filter_vector is None:
        if hasattr(payload, 'filter_vector'):
            vector = payload.filter_vector
    elif isinstance(filter_vector, int):
        vector = filter_vector
    tmp_node = FilterableIntervalTreeNode(tmp_interval, payload, vector)
    return tmp_node


class FilterableIntervalTreeNode(RBTreeNode):

    def __init__(self, key: Interval, payload=None, filter_vector: int = None):
        self.key = key,
        self.payload = payload or None
        if key is not None:
            self.subtree_maximum = key.end

        if hasattr(payload, 'qualifies'):
            self.qualifies = payload.qualifies
        else:
            self.qualifies = payload.__eq__

        if filter_vector is None:
            if hasattr(payload, 'filter_vector'):
                self.filter_vector = payload.filter_vector
            else:
                self.filter_vector = generate_basic_filter_vector(str(payload))
        else:
            self.filter_vector = filter_vector
        self.subtree_filter_vector = self.filter_vector
        super().__init__(key)

    def __contains__(self, item: 'FilterableIntervalTreeNode'):
        return check_contains(self, item)


class FilterableIntervalTree(RBTree):

    def __init__(self):
        super().__init__()
        self.nil = FilterableIntervalTreeNode(None, None, 0)
        self.nil.black = True
        self.nil.tree = self
        self.nil.subtree_maximum = -math.inf
        self.root = self.nil


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
    rb_lr(tree, node)
    update_subtree_filter_vector(node)
    update_subtree_filter_vector(node.parent)
    update_subtree_max_after_rotate(node)
    return node


def right_rotate(tree: FilterableIntervalTree, node: FilterableIntervalTreeNode):
    rb_rr(tree, node)
    update_subtree_filter_vector(node)
    update_subtree_filter_vector(node.parent)
    update_subtree_max_after_rotate(node)
    return node


def add_node(tree: FilterableIntervalTree, node: FilterableIntervalTreeNode) -> FilterableIntervalTreeNode:
    node.tree = tree
    node.left_child = node.right_child = tree.nil
    end = node.key.end
    begin = node.key.begin
    if tree.root is tree.nil:
        tree.root = node
        node.parent = tree.nil
        node.black = True
        return node

    current_node = last_parent = tree.root
    going_left = None
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
    no_updates = 0
    while parent is not tree.nil and no_updates < 400:
        expected_max = max(
            parent.key.end,
            parent.left_child.subtree_maximum,
            parent.right_child.subtree_maximum
        )

        expected_sfv = \
            parent.left_child.subtree_filter_vector | \
            parent.right_child.subtree_filter_vector | \
            parent.filter_vector

        needs_update = (expected_max != parent.subtree_maximum) or \
                       (expected_sfv != parent.subtree_filter_vector)

        if needs_update:
            parent.subtree_maximum = expected_max
            parent.subtree_filter_vector = expected_sfv
        else:
            no_updates += 1

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
            # TODO figure out how to update SFV and max only when a node is removed from a particular subtree
            # y.subtree_filter_vector = z.right_child.subtree_filter_vector | y.filter_vector

        y.left_child = z.left_child
        y.left_child.parent = y
        # y.subtree_filter_vector |= z.left_child.subtree_filter_vector
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


def query_tree(
        tree: FilterableIntervalTree,
        query_node: FilterableIntervalTreeNode,
        must_contain=True,
        ) -> Generator[FilterableIntervalTreeNode, None, None]:

    tree_root = tree.root
    tree_nil = tree.nil
    if tree_root is tree_nil:
        return

    query_interval = query_node.key
    query_interval_begin = query_interval.begin
    query_interval_end = query_interval.end
    query_fv = query_node.filter_vector

    payload_qualifier = query_node.qualifies

    track = 0

    search_queue = deque()
    search_queue.append(tree_root)
    interval_operation = interval_contains if must_contain else interval_overlaps
    not_root = False
    while search_queue:
        track += 1
        current_node = search_queue.pop()
        current_node_qualifies = interval_operation(current_node.key, query_interval)
        payload_qualifies = payload_qualifier(current_node.payload)

        if payload_qualifies is NotImplemented:
            payload_qualifies = query_node.filter_vector & current_node.filter_vector == query_node.filter_vector

        if current_node_qualifies and payload_qualifies:
            yield current_node

        left_child = current_node.left_child
        right_child = current_node.right_child

        left_ok = left_child is not tree_nil and \
            left_child.subtree_maximum >= query_interval_begin

        left_ok &= (query_fv & left_child.subtree_filter_vector == query_fv)

        right_ok = right_child is not tree_nil and \
            right_child.subtree_maximum >= query_interval_begin

        if must_contain and not_root:
            # TODO there's another relationship that can be used to filter here
            right_ok &= right_child.subtree_maximum >= query_interval_end

        right_ok &= (query_fv & right_child.subtree_filter_vector == query_fv)

        if right_ok:
            search_queue.append(right_child)

        if left_ok:
            search_queue.append(left_child)

        not_root = True


def adjust_payload(tree: FilterableIntervalTree,
                   a_node: FilterableIntervalTreeNode,
                   adjustment_interval: Interval,
                   adjustments: dict,
                   filter_vector_generator: Callable[[dict], int]=None)\
        -> List[FilterableIntervalTreeNode]:
    """
    Adjusts the payload of a node int its tree
    :param tree: tee to be adjusted
    :param a_node: node to adjust
    :param adjustment_interval: the interval for which we would like to see the adjustments made
    :param adjustments: the changes that we want to see made to the node's payload (only works for dictionaries)
    :param filter_vector_generator: a function that returns a filter vector for each payload
    :return: None
    """

    if filter_vector_generator is None:
        filter_vector_generator = lambda x: a_node.filter_vector

    old_interval = a_node.key
    remaining_intervals = old_interval.remove(adjustment_interval)

    new_payload = a_node.payload.copy()
    relevant_keys = adjustments.keys()
    for key in relevant_keys:
        old_property_value = new_payload.get(key)
        if isinstance(old_property_value, numbers.Number):
            new_payload[key] += adjustments[key]
        else:
            new_payload[key] = adjustments[key]

    filter_vector = filter_vector_generator(new_payload)
    remaining_nodes = \
        [FilterableIntervalTreeNode(_, a_node.payload.copy(), a_node.filter_vector) for _ in remaining_intervals]
    new_node = FilterableIntervalTreeNode(adjustment_interval, new_payload, filter_vector)

    result_list = [new_node] + remaining_nodes
    result_list = sorted(result_list, key=lambda node: node.key)

    added_nodes = set()

    first_item = result_list[0]
    last_item = result_list[-1]
    first_payload = first_item.payload
    last_payload = last_item.payload

    pre_node = get_predecessor_for_node(tree, a_node, qualifier=lambda x: x == first_payload)
    post_node = get_successor_for_node(tree, a_node, qualifier=lambda x: x == last_payload)

    delete_node(tree, a_node)

    if pre_node and Interval.touches(pre_node.key, first_item.key) and pre_node.payload == first_item.payload:
        consolidate_nodes(pre_node, first_item, tree)
        added_nodes.add(first_item)

    if post_node and Interval.touches(post_node.key, last_item.key) and post_node.payload == last_item.payload:
        consolidate_nodes(last_item, post_node, tree)
        added_nodes.add(last_item)

    for node in result_list:
        if node not in added_nodes:
            add_node(tree, node)

    return new_node

#     0(a)
# -1(c)  3(a)
#     2(b)  4(a)


def get_predecessor_for_node(
        tree: FilterableIntervalTree,
        node: FilterableIntervalTreeNode,
        qualifier: Callable[[Any], bool]=None,
        filter_vector=None) -> FilterableIntervalTreeNode:

    tree_nil = tree.nil
    if qualifier is None:
        qualifier = lambda x: node.payload == x

    current = node
    exhausted = False

    while not exhausted:
        if current.left_child is not tree_nil:
            inspect_left_child = True
            if filter_vector:
                collision = filter_vector & current.left_child.subtree_filter_vector
                inspect_left_child = filter_vector == collision

            if inspect_left_child:
                result = get_maximum_node(tree, current.left_child, qualifier)
                if result:
                    return result

        if current.parent is not tree_nil and current is current.parent.right_child:
            if qualifier(current.parent.payload):
                return current.parent
            if current.parent.left_child is not tree_nil:
                result = get_maximum_node(tree, current.parent.left_child, qualifier)
                if result:
                    return result

        while current.parent is not tree_nil and current.parent.left_child is current:
            current = current.parent

        if current.parent is tree_nil:
            exhausted = True
        # I am the right child
        current = current.parent
        if qualifier(current.payload):
            return current

    return None

#           5(a)
#       3(b)    6(c)
#                  9(d)
#                     15(e)
# get_maximum_node("5(a)", "d" ) == 9(d)


def get_maximum_node(
        tree: FilterableIntervalTree,
        node: FilterableIntervalTreeNode,
        qualifier: Callable[[Any], bool]
) -> FilterableIntervalTreeNode:
    stack = deque([node])
    while node.right_child is not tree.nil:
        stack.append(node.right_child)
        node = node.right_child

    candidate = stack.pop()
    while not qualifier(candidate.payload):
        if candidate.left_child is not tree.nil:
            stack.append(candidate.left_child)
            node = candidate.left_child
            while node.right_child is not tree.nil:
                stack.append(node.right_child)
                node = node.right_child
        if stack:
            candidate = stack.pop()
        else:
            return None

    return candidate


def get_successor_for_node(
        tree: FilterableIntervalTree,
        node: FilterableIntervalTreeNode,
        qualifier: Callable[[Any], bool]=None,
        filter_vector=None) \
        -> FilterableIntervalTreeNode:

    tree_nil = tree.nil
    if qualifier is None:
        qualifier = lambda x: node.payload == x

    current = node
    exhausted = False
    result = None

    while not exhausted:
        if current.right_child is not tree_nil:
            inspect_right_child = True
            if filter_vector:
                collision = filter_vector & current.left_child.subtree_filter_vector
                inspect_right_child = filter_vector == collision

            if inspect_right_child:
                result = get_maximum_node(tree, current.right_child, qualifier)
                if result:
                    return result

            if result:
                return result
        if current.parent is not tree_nil and current is current.parent.left_child:
            if qualifier(current.parent.payload):
                return current.parent
            if current.parent.right_child is not tree_nil:
                result = get_maximum_node(tree, current.parent.right_child, qualifier)
                if result:
                    return result

        while current.parent is not tree_nil and current.parent.right_child is current:
            current = current.parent

        if current.parent is tree_nil:
            exhausted = True
        # I am the left child
        current = current.parent
        if qualifier(current.payload):
            return current

    return None


def get_minimum_node(
        tree: FilterableIntervalTree, node: FilterableIntervalTreeNode, qualifier: Callable[[Any], bool]
) -> FilterableIntervalTreeNode:
    stack = deque([node])
    while node.left_child is not tree.nil:
        stack.append(node.left_child)
        node = node.left_child

    candidate = stack.pop()
    while not qualifier(candidate.payload):
        if candidate.right_child is not tree.nil:
            stack.append(candidate.right_child)
            node = candidate.right_child
            while node.left_child is not tree.nil:
                stack.append(node.left_child)
                node = node.left_child
        if stack:
            candidate = stack.pop()
        else:
            return None

    return candidate


def consolidate_nodes(pre_node: FilterableIntervalTreeNode,
                      post_node: FilterableIntervalTreeNode,
                      tree: FilterableIntervalTree) \
        -> FilterableIntervalTreeNode:

    new_interval = Interval(pre_node.key.begin, post_node.key.end)
    new_node = FilterableIntervalTreeNode(new_interval, pre_node.payload, pre_node.filter_vector)

    if pre_node.tree is tree:
        delete_node(tree, pre_node)

    if post_node.tree is tree:
        delete_node(tree, post_node)

    add_node(tree, new_node)
    return new_node
