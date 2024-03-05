
# 把req转换成字典格式，方便取值
req_dict = json.loads(req)
# 把resp也转为字典
resp_dict = json.loads(resp)

# print(resp_dict)

with open("mark_down.md", 'w', encoding="utf8") as file:
    file.write(header("大卡接口文档", 1) + "\n")
    file.write(header("接口一：", 2) + "\n")
    file.write(header("接口协议", 3) + "\n")
    file.write(bold("协议:") + "  https POST json \n \n")
    file.write(header("请求参数", 3) + "\n")

    # 请求参数
    req_keys_list = ["通用字段encType、nonce、signType、timeStamp、sign \n"]
    # 从req 的第六个key开始，加入req_keys_list,只要key
    for key in list(req_dict)[5:]:
        req_keys_list.append(key + ": \n")
    file.write(ordered_list(req_keys_list))
    file.write("\n 示例（包括通用字段）：\n")

    file.write(code_block(f"{req}", "json") + "\n")
    file.write(header("回包字段", 3) + "\n")
    file.write(code_block(f"{resp}", "json") + "\n")

    file.write("\n 返回字段说明：\n\n")
    # resp_dict里面有很多的key-value对，将所有的key放入keys_list当中，并且同时将每个key对应的value的类型以字符串的方式写入type_list中
    keys_list = ["参数名"]
    type_list = ["数据类型"]
    # 解析回包
    for k, v in resp_dict.items():
        keys_list.append(k)
        type_list.append(typeName(v))
        # 如果v的类型是list，继续解析
        if isinstance(v, list):
            for i in v:
                if isinstance(i, dict):
                    for j in i.keys():
                        if j in keys_list:
                            continue
                        keys_list.append(j)
                        type_list.append(typeName(i[j]))
                else:
                    if j in keys_list:
                        continue
                    keys_list.append(i)
                    type_list.append(typeName(i))

    file.write(table([keys_list,
                      type_list,
                      ["说明"]
                      ]))
    file.write("\n\n")
    file.write(header("异常处理", 4) + "\n")
    file.write("系统返回码定义：\n")
    file.write("\n")
    file.write("注意，失败一定要返回非0\n")

    file.write(header("签名算法", 3) + "\n")
    file.write("1.对除了sign以外的参数按照key=value的格式，并按照参数名ASCII字典序排序，用&拼接。\n\n")
    file.write("例如转换后为：\n\n")
    file.write(code_block(" ", "json") + "\n\n")
    file.write("2.上面的字符串拼接上token，token私下约定。这里是\n\n")
    file.write(code_block(" ", "json") + "\n\n")
    file.write("3.对第2步得到的字符串计算sha1。结果形式为大写的16进制字符串。\n\n")
    file.write(code_block("4850BEEA47C2AD35F8A5830A8C83872D34393BD9", "json") + "\n\n")
    file.write("4.将结果填到请求的 sign 字段。\n\n")

    file.write("\n")

# 定义输入和输出文件的路径
input_file = 'mark_down.md'
output_file = 'example.docx'

# pypandoc.convert_file(input_file, 'docx', outputfile=output_file)

# 构建 Pandoc 命令
command = f'pandoc -s {input_file} -o {output_file} --highlight-style=kate'

# 运行命令
subprocess.run(command, shell=True)

'''

'''