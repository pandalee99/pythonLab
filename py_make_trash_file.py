import os

# print(os.getcwd())

file_path = "file.txt"  # 替换为你想要保存文件的路径
target_size = 512 * 1024 * 1024  # 512MB

with open(file_path, "wb") as file:
    while file.tell() < target_size:
        file.write(b"This is a sample line.\n")