# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import json


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


def python_to_json() -> str:
    """ 将python对象转换成json """
    d = {
        'name': 'python"书籍"',
        'price': 62.3,
        'is_valid': True
    }
    rest = json.dumps(d, ensure_ascii=False)
    print(rest)
    return rest


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    python_to_json()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
