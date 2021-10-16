import os


def sort_like_explorer(dir_path: str) -> tuple[list[str], list[str]]:
    dirs, files = [], []
    dir_and_file_list = os.listdir(dir_path)
    dir_and_file_list.sort()
    dir_and_file_list.sort(key=lambda x: len(x))

    # first dirs and then files
    for item in dir_and_file_list:
        if os.path.isfile(os.path.join(dir_path, item)):
            files.append(item)
        elif os.path.isdir(os.path.join(dir_path, item)):
            dirs.append(item)

    return dirs, files
