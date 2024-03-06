
# 把req转换成字典格式，方便取值
req_dict = json.loads(req)
# 把resp也转为字典
resp_dict = json.loads(resp)

# print(resp_dict)

def typeName(v):
    name = type(v).__name__
    if name == 'dict':
        return "Json"
    if name == "str":
        return "string"
    else:
        return name




def makeTable(req_dict, resp_dict):
    file.write(header("接口：", 2) + "\n")
    file.write(header("接口协议", 3) + "\n")
    file.write(bold("协议:") + "  https POST json \n \n")
    file.write(header("请求参数", 3) + "\n")
    req = json.dumps(req_dict, indent=4, separators=(',', ': '), ensure_ascii=False)

    resp= json.dumps(resp_dict, indent=4, separators=(',', ': '), ensure_ascii=False)

    # 请求参数
    req_keys_list = ["通用字段encType、nonce、signType、timeStamp、sign \n"]
    # 从req 的第六个key开始，加入req_keys_list,只要key
    for key in list(req_dict)[5:]:
        req_keys_list.append(key + ": \n")
    file.write(ordered_list(req_keys_list))
    file.write("\n 示例（包括通用字段）：\n")
    file.write("\n 请求字段：\n")

    file.write(code_block(f"{req}", "json") + "\n\n\n")
    file.write("\n 回包字段：\n")
    file.write(code_block(f"{resp}", "json") + "\n")

    file.write("\n 返回字段说明：\n\n")
    # resp_dict里面有很多的key-value对，将所有的key放入keys_list当中，并且同时将每个key对应的value的类型以字符串的方式写入type_list中
    def collect_values(data, path, keys_list, type_list):
        if isinstance(data, dict):
            for key, value in data.items():
                new_path = f"{path}.{key}" if path else key
                keys_list.append(new_path)
                type_list.append(typeName(value))
                collect_values(value, new_path, keys_list, type_list)
        elif isinstance(data, list):
            for index, item in enumerate(data):
                new_path = f"{path}"
                keys_list.append(new_path)
                type_list.append(typeName(item))
                collect_values(item, new_path, keys_list, type_list)

    keys_list = ["参数名"]
    type_list = ["数据类型"]
    # 解析回包
    collect_values(resp_dict, "", keys_list, type_list)

    file.write(table([keys_list,
                      type_list,
                      ["说明"]
                      ]))
    file.write("\n\n")
    file.write(header("异常处理", 3) + "\n")
    file.write("系统返回码定义：https://docs.qq.com/doc/DSWRobWpHa3BhY0Vn \n")
    file.write("\n")
    file.write("注意，失败一定要返回非0\n\n")

    file.write(header("签名算法", 3) + "\n")
    file.write("1.对除了sign以外的参数按照key=value的格式，并按照参数名ASCII字典序排序，用&拼接。\n\n")
    file.write("例如转换后为：\n\n")

    # 从req_dict中删除sign参数
    req_dict.pop("sign", None)
    # 对参数名进行排序
    sorted_keys = sorted(req_dict.keys())
    # 按照key=value的格式拼接参数
    params = [f"{key}={req_dict[key]}" for key in sorted_keys]
    # 使用'&'符号拼接参数
    result = '&'.join(params)

    file.write(code_block(f"{result}", "json") + "\n\n")
    file.write("2.上面的字符串拼接上token，token私下约定。这里是\n\n")
    result = result+"&token=xxx&type=1"
    file.write(code_block(f"{result}", "json") + "\n\n")
    sha1_hash = hashlib.sha1()
    sha1_hash.update(result.encode('utf-8'))
    result = sha1_hash.hexdigest().upper()
    file.write("3.对第2步得到的字符串计算sha1。结果形式为大写的16进制字符串。\n\n")
    file.write(code_block(f"{result}", "json") + "\n\n")
    file.write("4.将结果填到请求的 sign 字段。\n\n")
    file.write("\n")


with open("mark_down.md", 'w', encoding="utf8") as file:
    file.write(header("大卡接口文档", 1) + "\n")
    req_dict_list = [json.loads(req), json.loads(req1), json.loads(req2)]
    resp_dict_list = [json.loads(resp), json.loads(resp1), json.loads(resp2)]
    for i, data in enumerate(req_dict_list):
        makeTable(req_dict_list[i], resp_dict_list[i])

# 定义输入和输出文件的路径
input_file = 'mark_down.md'
output_file = 'example.docx'

# pypandoc.convert_file(input_file, 'docx', outputfile=output_file)

# 构建 Pandoc 命令
command = f'pandoc -s {input_file} -o {output_file}  --reference-doc=style.docx'

# 运行命令
subprocess.run(command, shell=True)

'''

'''