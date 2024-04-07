import hashlib
import json
import os
import time

from io import BytesIO
from venv import logger


async def upload_py_fd(dst_dir_name, dst_basename, f, mode=0o640):
    Base_Url = ""

    def split_file(file, chunk_size=1024):
        print(f.getbuffer().nbytes)
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            yield chunk

    # 生成一个随机的 UUID
    random_uuid = uuid.uuid4()
    # 如果传过来的是bytes，则需要转为file
    if isinstance(f, bytes):
        f = BytesIO(f)
    total_size = f.getbuffer().nbytes
    logger.info("the file byte total size is  %s " % total_size)

    # md5
    def calculate_md5(file_object):
        hash_object = hashlib.md5()
        for chunk in iter(lambda: file_object.read(4096), b""):
            hash_object.update(chunk)
        file_object.seek(0)  # 将文件指针重置到文件的开始位置
        return hash_object.hexdigest()

    # 假设你已经有了文件对象 f
    md5 = calculate_md5(f)

    # 分片大小，可自定义
    # 表示1kb
    chunk_size = 1024
    # 表示  25MB
    chunk_size = chunk_size * 25 * 1024

    # resp
    resp_dict = {}

    # 分割文件
    for i, chunk in enumerate(split_file(f, chunk_size=chunk_size)):
        logger.info(f"Chunk index is : {i + 1},  the chunk is : {chunk}")
        f = BytesIO(chunk)

        data = {
            "dzuuid": str(random_uuid),
            "dzchunkindex": str(i),
            "dztotalfilesize:": str(len(chunk)),
            "dzchunksize:": str(chunk_size),
            "dztotalchunkcount": str((total_size - 1) // chunk_size + 1),
            "dzchunkbyteoffset": str(i * chunk_size),
            "md5": str(md5),
            "file": f,
            "file_name": dst_basename,
            "upload_type": str(1)  # 分类型 0代表使用 time.time()_file_name ，1 代表只使用file_name
        }

        logger.info("post data info : %s" % data)

        http_code, resp_buff = await apost(setting.DOMAIN + Base_Url + dst_dir_name, data=data)
        logger.info("http code info  %s" % http_code)
        logger.info("resp is  about wfs url  %s" % resp_buff)
        if http_code != 200:
            raise print()
            # raise ErrMsgError("upload version code:%s" % http_code)
        else:
            resp_dict.update(resp_buff)

    return resp_dict


# 创建一个BytesIO对象
buff = b"some large data" * 100
f = BytesIO(buff)
# print(f.read())


upload_py_fd(dst_basename="", dst_dir_name="file", f=f)


async def get_file_md5(file_path):
    hash_md5 = hashlib.md5()
    async with aiofiles.open(file_path, "rb") as f:
        while True:
            chunk = await f.read(409600)
            hash_md5.update(chunk)
            if chunk == b"":
                break
    return hash_md5.hexdigest()


from flask import request, Response


async def slice_upload_wfs(path):
    # 权限校验和检测

    #
    res = {}
    req_body = await request.form
    files = await request.files
    logger.info("show json req_body:%s, file:%s" % (req_body, files))
    file = files.get("file", None)
    if not file:
        return Response("not file", 400, content_type="text/html; charset=UTF-8")
    offset = int(req_body.get("dzchunkbyteoffset", 0))
    md5 = req_body.get("md5", "")
    idx = int(req_body.get("dzchunkindex", 0))
    block_num = int(req_body.get("dztotalchunkcount", 0))
    uuid = req_body.get("dzuuid", "")
    name = file.filename
    logger.info("origin file name info %s " % name)
    logger.info(" info : %s" % req_body)
    if name == "file":
        # 如果传有别名，就使用别名，接口适配
        name = req_body.get("file_name", "file")
        logger.info("now , the file name is %s " % name)

    tmp_full_path = os.path.join(UPLOAD_TEMP_PATH, "%s_%s" % (str(uuid), name))
    logger.info(f' slice_upload_wfs Processing {name}')
    if idx == 0 and os.path.exists(tmp_full_path):
        # 文件传输失败后重新上传，清空前面失败的
        os.remove(tmp_full_path)
    with open(tmp_full_path, "ab") as f:
        f.seek(offset)
        f.write(file.stream.read())

    if idx + 1 == block_num:
        t1 = time.time()
        local_md5 = await get_file_md5(tmp_full_path)
        logger.info("calc md5! cost:%s" % (time.time() - t1,))
        if md5 == local_md5:
            try:
                upload_type = int(req_body.get("upload_type", 0))  # 分类型 0代表使用 time.time()_file_name ，1 代表只使用file_name
                if upload_type == 1:
                    wfs_target_path = os.path.join(WFS_BASE_PATH, path, "%s" % (str(name)))
                else:
                    wfs_target_path = os.path.join(WFS_BASE_PATH, path, "%s_%s" % (str(int(time.time() * 1000)), name))
                t1 = time.time()
                await wfs_upload(client, tmp_full_path, wfs_target_path, overwrite=True)
                logger.info("end upload! cost:%s" % (time.time() - t1,))
            except Exception as e:
                logger.info("slice_upload_wfs Traceback:%s" % e)
                return Response(e.args[0], 400, content_type="text/html; charset=UTF-8")
            finally:
                os.remove(tmp_full_path)
            res[name] = wfs_target_path
        else:
            if os.path.exists(tmp_full_path):
                # 清理失败的文件
                os.remove(tmp_full_path)
            logger.info("Traceback md5 is not equal :%s  %s" % (md5, local_md5))
            return Response(" %s md5:%s check fail!" % (tmp_full_path, md5), 500,
                            content_type="text/html; charset=UTF-8")
    return Response(json.dumps(res), 200, content_type="application/json; charset=UTF-8")
