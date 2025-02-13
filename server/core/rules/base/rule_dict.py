class RuleDict:

    def __init__(self):
        self._entries = dict()

    def _verify_key(self, item):
        if type(item) is not str:
            raise ValueError('RuleDict only supports string keys.')

    def __contains__(self, item):
        self._verify_key(item)
        return item.lower() in self._entries

    def __getitem__(self, item):
        self._verify_key(item)
        return self._entries[item.lower()]

    def __setitem__(self, key, value):
        self._verify_key(key)
        self._entries[key.lower()] = value
