from functions.get_song import get_song


class Queueue:  # класс очереди (почти ничего не делает, можно было и без него обойтись, но переписывать уже поздно)
    def __init__(self):
        self.list = []
        self.current = ''

    def __getitem__(self, item):
        return self.list[item]

    def pop(self, item):
        return self.list.pop(item)

    def is_empty(self):
        return True if not self.list else False

    def add(self, query):
        song = get_song(query)
        if song is None:
            return 0
        else:
            self.list.append(song)
            return song

    def clear(self):
        self.list = []

    def __len__(self):
        return len(self.list)