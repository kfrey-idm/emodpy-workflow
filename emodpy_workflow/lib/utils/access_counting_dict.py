from typing import Any


class AccessCountingDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.access_count = {}

    def access_count_for_key(self, k: Any):
        counts = self.access_count.get(k, 0)
        return counts

    def _tally_access(self, k):
        if k not in self.access_count:
            self.access_count[k] = 0
        self.access_count[k] += 1
        # print(f"New count: key: {k} count: {self.access_count[k]}")

    def __getitem__(self, k):
        self._tally_access(k=k)
        value = super().__getitem__(k)
        return value

    def get(self, k, *args, **kwargs):
        self._tally_access(k=k)
        value = super().get(k, *args, **kwargs)
        return value

    def pop(self, k, *args, **kwargs):
        self._tally_access(k=k)
        value = super().pop(k, *args, **kwargs)
        return value

    @classmethod
    def from_dict(cls, d: dict):
        return cls(**d)


# TODO: move/add to these tests in the tests dir


if __name__ == '__main__':
    # d = AccessCountingDict(**{'a': 1, 'b': 2})
    d = AccessCountingDict.from_dict({'a': 1, 'b': 2})

    # [] access tests
    print('--- [] tests')
    print(f"d['a'] = {d['a']}")
    print(f"d['b'] = {d['b']}")
    try:
        d['c']
    except KeyError as e:
        print(f"No such key d['c'], as expected")

    # get() access tests
    print('--- .get() tests')
    print(f"d.get('a') = {d.get('a')}")
    print(f"d.get('a', 99) = {d.get('a', 99)}")
    print(f"d.get('b') = {d.get('b')}")
    print(f"d.get('b', 99) = {d.get('b', 99)}")
    print(f"d.get('c') = {d.get('c')}")
    print(f"d.get('c', 99) = {d.get('c', 99)}")

    # pop() access tests
    print('--- .pop() tests')
    print(f"d.pop('a') = {d.pop('a')}")
    try:
        d.pop('a')
    except KeyError as e:
        print(f"No such key d.pop('a'), as expected")
    print(f"d.get('a') = {d.get('a')}")
    try:
        d['a']
    except KeyError as e:
        print(f"No such key d['a'], as expected")

    print("d['a'] = 1")
    d['a'] = 1
    print(f"d.pop('a', 99) = {d.pop('a', 99)}")
    print(f"d.pop('a', 99) = {d.pop('a', 99)}")
    print(f"d.get('a') = {d.get('a')}")
    try:
        d['a']
    except KeyError as e:
        print(f"No such key d['a'], as expected")

    print(f"All access counts: {d.access_count}")