import logging


def test():
    with open("./test.txt", 'w') as f:
        for i in range(1, 11):
            data = "test"
            f.write(data)
