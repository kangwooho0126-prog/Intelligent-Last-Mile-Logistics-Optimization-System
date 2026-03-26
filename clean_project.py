import os

# 需要删除的文件后缀
UNWANTED_EXTENSIONS = [
    ".pyc",
    ".pyo",
    ".log"
]

# 需要删除的文件名
UNWANTED_FILES = [
    ".DS_Store"
]

# 需要删除的文件夹
UNWANTED_DIRS = [
    "__pycache__",
    ".ipynb_checkpoints"
]

# 判断是否为空文件（大小为0）
def is_empty_file(filepath):
    return os.path.isfile(filepath) and os.path.getsize(filepath) == 0


def clean_project(root_dir):
    print(f"🧹 Cleaning project at: {root_dir}\n")

    for root, dirs, files in os.walk(root_dir, topdown=False):

        # 删除文件
        for name in files:
            filepath = os.path.join(root, name)

            # 删除无用扩展文件
            if any(name.endswith(ext) for ext in UNWANTED_EXTENSIONS):
                print(f"🗑 Deleting file: {filepath}")
                os.remove(filepath)
                continue

            # 删除指定文件
            if name in UNWANTED_FILES:
                print(f"🗑 Deleting file: {filepath}")
                os.remove(filepath)
                continue

            # 删除空文件
            if is_empty_file(filepath):
                print(f"🗑 Deleting empty file: {filepath}")
                os.remove(filepath)

        # 删除文件夹
        for name in dirs:
            dirpath = os.path.join(root, name)

            if name in UNWANTED_DIRS:
                print(f"🗑 Deleting directory: {dirpath}")
                try:
                    os.rmdir(dirpath)
                except:
                    # 如果非空，用这个强删
                    import shutil
                    shutil.rmtree(dirpath)


if __name__ == "__main__":
    project_root = os.getcwd()
    clean_project(project_root)

    print("\n✅ Clean complete!")