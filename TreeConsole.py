import os

def print_directory_tree(startpath, prefix=""):
    """Рекурсивно печатает структуру файлового дерева."""
    # Получаем список элементов в каталоге
    items = os.listdir(startpath)
    items.sort()  # Сортируем для удобства отображения

    # Получаем количество подкаталогов для корректного отображения
    count = len(items)
    
    for i, item in enumerate(items):
        path = os.path.join(startpath, item)
        is_last = (i == count - 1)  # Является ли текущий элемент последним в списке

        if os.path.isdir(path):
            connector = "╚══" if is_last else "╠═══╗"
            print(f"{prefix}{connector}{item}/") # Выводим каталог
            new_prefix = prefix + ("║   " if not is_last else "    ")  # Обновляем префикс
            print_directory_tree(path, new_prefix)  # Рекурсивный вызов
        else:
            connector = "╚═" if is_last else "╠══"
            print(prefix + connector + item)  # Выводим файл
def main():
    directory = input("Введите путь к каталогу: ")
    if os.path.isdir(directory):
        print(f"Содержимое каталога: {directory}")
        print_directory_tree(directory)
    else:
        print("Указанный путь не является каталогом.")

if __name__ == "__main__":
    main()