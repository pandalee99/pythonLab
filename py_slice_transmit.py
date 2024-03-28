from io import BytesIO


def upload_py_fd_opt(dst_dir_name, dst_basename, f, mode=0o640):
    files = {
        dst_basename: f
    }
    Base_Url = ""
    path = ""

    from io import BytesIO

    def split_file(file, chunk_size=1024):
        print(f.getbuffer().nbytes)
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            yield chunk

    import uuid

    # 生成一个随机的 UUID
    random_uuid = uuid.uuid4()
    total_size = f.getbuffer().nbytes
    print(total_size)

    # md5
    import hashlib
    def calculate_md5(file_object):
        hash_object = hashlib.md5()
        for chunk in iter(lambda: file_object.read(4096), b""):
            hash_object.update(chunk)
        file_object.seek(0)  # 将文件指针重置到文件的开始位置
        return hash_object.hexdigest()

    # 假设你已经有了文件对象 f
    md5 = calculate_md5(f)

    chunk_size = 1024

    # 分割文件
    for i, chunk in enumerate(split_file(f, chunk_size=chunk_size)):
        print(f"Chunk {i + 1}: {chunk}")
        data = {
            "dzuuid": random_uuid,
            "dzchunkindex": str(i),
            "dztotalfilesize:": str(len(chunk)),
            "dzchunksize:": str(chunk_size),
            "dztotalchunkcount": str((total_size - 1) // chunk_size + 1),
            "dzchunkbyteoffset": str(i * chunk_size),
            "md5": md5,
            # file: (binary)
        }
        file = BytesIO(chunk)
        files = {'file': file}

        print(data)
        print(files)


# 创建一个BytesIO对象
buff = b"some large data" * 100
f = BytesIO(buff)
# print(f.read())


upload_py_fd_opt(dst_basename="", dst_dir_name="file", f=f)
