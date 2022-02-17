import time

MISSING = object()


class TimedData:
    def __init__(self, data, expiry) -> None:
        self._data = data
        self._expiry = expiry
        self._has_expired = False
        self._life = time.time() + expiry

    def _refresh(self):
        if self._life > time.time():
            self._has_expired = False
            return
        if not self._has_expired:
            self._has_expired = True
            # At this point, the data can be safely deleted
            # We made this if check because we don't want to attempt to delete
            # the data if it has already been deleted
            del self._data

    @property
    def has_expired(self):
        self._refresh()
        return self._has_expired

    @property
    def value(self):
        self._refresh()
        if self._has_expired:
            raise ValueError("Data has expired")
        return self._data

    @property
    def data(self):  # An alias for value
        return self.value

    @property
    def time_left(self):
        self._refresh()
        return self._life - time.time()

    def refresh(self):
        self._refresh()


class Interim:
    def __init__(self, bot) -> None:
        self.bot = bot
        self.data = []
        self.dictionary_data = {}

    def add(self, new_data, expiry, *, key=MISSING):
        if key is MISSING:
            self.data.append(TimedData(new_data, expiry))
            return len(self.data) - 1  # The index of the data

        if key in self.dictionary_data:
            raise KeyError(f"Key {key} already exists")
        self.dictionary_data[key] = TimedData(new_data, expiry)

    def __getitem__(self, key):
        # Only works if the key is in the dictionary
        if key in self.dictionary_data:
            return self.dictionary_data[key].value
        raise KeyError(f"Key {key} not found")

    def get_list(self):
        return [i.value for i in self.data if not i.has_expired]

    def get_time_object_list(self):
        return [i for i in self.data]

    def get_item(self, key):
        return self.dictionary_data[key].value

    def get_time_left(self, key):
        return self.dictionary_data[key].time_left

    def refresh_key(self, key):
        self.dictionary_data[key].refresh()

    def clear_list(self):
        self.data = []

    def clear_dictionary(self):
        self.dictionary_data = {}
