import os


def get_extensions(_items):
    return sorted(
        set([os.path.splitext(os.path.basename(item[1]))[1].lower() for item in _items])
    )


def get_number_of_items(_file):
    with open(_file, "r") as f:
        return sum(1 for line in f)


def get_txt_files(_path):
    return [
        os.path.join(_path, x)
        for x in os.listdir(_path)
        if os.path.splitext(x)[1].lower() == ".txt"
    ]
