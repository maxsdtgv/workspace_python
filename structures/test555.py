number = 5


def myfunc():
    # Выводит 5
    print(number)


def anotherfunc():
    # Это вызывает исключение, поскольку глобальная апеременная
    # не была вызванна из функции. Python в этом случае создает
    # одноименную переменную внутри этой функции и доступную
    # только для операторов этой функции.
    number = 3
    print(number)


def yetanotherfunc():
    global number
    # И только из этой функции значение переменной изменяется.

    print(number)
    number = 4

def newfunc():
    # Выводит 5
    print(number)

myfunc()
anotherfunc()
yetanotherfunc()
newfunc()
