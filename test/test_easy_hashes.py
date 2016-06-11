from intervaltree import easy_hashes
import hashlib
import struct
import string
import random


def id_generator(size=6, chars=string.ascii_uppercase + string.digits) -> str:
    return ''.join(random.choice(chars) for _ in range(size))


def assert_0_to_63(value):
    assert value >= 0
    assert value < 64


def test_hashalg_to_64():
    random.seed('testing')
    seeds = list(
        map(id_generator, range(0, 300))
    )

    for seed in seeds:
        data = easy_hashes.hashalg_to_64(seed, count=4)
        for _ in data:
            assert_0_to_63(_)
        data = easy_hashes.hashalg_to_64(seed, hashlib.md5, 4)
        for _ in data:
            assert_0_to_63(_)


def test_hash_to_64():
    random.seed('testing')
    seeds = list(
        map(lambda _: id_generator(10), range(0, 300))
    )
    count = 6
    uniques_needed = count * 0.65
    for seed in seeds:
        data = easy_hashes.hash_to_64(seed, count=count)
        for _ in data:
            assert_0_to_63(_)
        uniques = set(data)
        assert len(uniques) >= uniques_needed
