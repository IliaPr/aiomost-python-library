class DotDict:
    def __init__(self, dictionary):
        for key, value in dictionary.items():
            # Если значение — тоже dict, преобразуем его рекурсивно
            if isinstance(value, dict):
                value = DotDict(value)
            setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)
