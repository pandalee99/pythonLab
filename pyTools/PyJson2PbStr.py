import json


# 这是一个json


resp = """
 {
   "id":3456789,
   "type":"donut",
   "name":"Cake",
   "ppu":0.55,
   "batters":
      [{"id":"1001","type":"Regular"}, {"id":"1002","type":"Chocolate"} ],
   "topping":
       ["Maple Syrup"]
    }
"""

# 把resp转为dict
resp_dict = json.loads(resp)

def u2c(value):
    # 使用split()函数将字符串按下划线分割
    # 使用title()函数将每个单词的首字母大写
    # 使用join()函数将单词重新组合
    # 使用replace()函数去掉空格

    return "".join(word.title() for word in value.split('_')).replace(" ", "")


def to_tuple_sorted(x):
    # 将字典或列表转换为元组，以便可以将其用作字典的键
    if isinstance(x, dict):
        return tuple((k, to_tuple_sorted(v)) for k, v in sorted(x.items()))
    elif isinstance(x, list):
        return tuple(to_tuple_sorted(v) for v in x)
    else:
        return x


def dict_to_proto(data, message_name="Example", indent=0, message_dict=None, root=True, root_messages=None,
                  context_set=None):
    # message_dict 用于存储已经处理过的消息类型，避免重复定义
    if message_dict is None:
        message_dict = {}
    # root_messages 用于存储根消息中的所有嵌套消息
    if root_messages is None:
        root_messages = []

    fields = ''
    i = 1
    for key, value in data.items():
        if isinstance(value, dict):
            # 如果值是字典，那么需要为它创建一个新的消息类型
            value_tuple = to_tuple_sorted(value)
            nested_message_name = key.capitalize()
            if value_tuple not in message_dict:
                # 如果这个消息类型还没有被定义过，那么需要定义它
                message_dict[value_tuple] = nested_message_name
                nested_message = dict_to_proto(value, message_name=nested_message_name, indent=indent,
                                               message_dict=message_dict, root=False, root_messages=root_messages,
                                               context_set=context_set)
                if nested_message not in context_set:
                    context_set[nested_message] = nested_message_name
                    root_messages.append(
                        ' ' * (indent + 2) + f'message {u2c(nested_message_name)} {{\n' + nested_message + ' ' * (
                                indent + 2) + '}\n')
            else:
                # 如果定义过了，修改一下名字就行了
                if value_tuple in message_dict:
                    nested_message_name = message_dict[value_tuple]
            fields += ' ' * (indent + 2) + f'optional {u2c(nested_message_name)} {u2c(key)} = {i};\n'
        elif isinstance(value, list):
            # 如果值是列表，那么需要为它创建一个新的消息类型
            if all(isinstance(item, dict) for item in value):
                value_tuple = to_tuple_sorted(value[0])
                nested_message_name = key.capitalize()
                if value_tuple not in message_dict:
                    message_dict[value_tuple] = nested_message_name
                    nested_message = dict_to_proto(value[0], message_name=nested_message_name, indent=indent,
                                                   message_dict=message_dict, root=False,
                                                   root_messages=root_messages, context_set=context_set)
                    root_messages.append(
                        ' ' * (indent + 2) + f'message {u2c(nested_message_name)} {{\n' + nested_message + ' ' * (
                                indent + 2) + '}\n')
                fields += ' ' * (indent + 2) + f'repeated {u2c(nested_message_name)} {u2c(key)} = {i};\n'
            else:
                fields += ' ' * (indent + 2) + f'repeated string {u2c(key)} = {i};\n'
        else:
            # 如果值是基本类型，那么直接添加字段
            if isinstance(value, int):
                fields += ' ' * (indent + 2) + f'optional int32 {u2c(key)} = {i};\n'
            else:
                fields += ' ' * (indent + 2) + f'optional string {u2c(key)} = {i};\n'
        i += 1

    if root:
        # 如果是根消息，那么需要添加所有的嵌套消息和字段
        proto_string = ' ' * indent + f'message {message_name} {{\n' + ''.join(
            root_messages) + fields + ' ' * indent + '}\n'
    else:
        # 如果不是根消息，那么只需要添加字段
        proto_string = fields
    return proto_string


def dict_to_proto_separate(data, message_name="Example", indent=0, message_dict=None,
                           context_set=None):
    if message_dict is None:
        message_dict = {}

    nested_messages = ''
    fields = ''
    i = 1
    for key, value in data.items():
        if isinstance(value, dict):
            value_tuple = to_tuple_sorted(value)
            nested_message_name = key.capitalize()
            if value_tuple not in message_dict:
                message_dict[value_tuple] = nested_message_name
                nested_message = dict_to_proto_separate(value, message_name=nested_message_name, indent=indent,
                                               message_dict=message_dict, context_set=context_set)
                if nested_message not in context_set:
                    context_set[nested_message] = nested_message_name
                    nested_messages += nested_message + '\n'
            else:
                # 如果定义过了，修改一下名字就行了
                if value_tuple in message_dict:
                    nested_message_name = message_dict[value_tuple]
            fields += ' ' * indent + f'optional {u2c(nested_message_name)} {u2c(key)} = {i};\n'
        elif isinstance(value, list):
            if all(isinstance(item, dict) for item in value):
                value_tuple = to_tuple_sorted(value[0])
                nested_message_name = key.capitalize()
                if value_tuple not in message_dict:
                    message_dict[value_tuple] = nested_message_name
                    nested_message = dict_to_proto_separate(value[0], message_name=nested_message_name, indent=indent,
                                                            message_dict=message_dict, context_set=context_set)
                    nested_messages += nested_message + '\n'
                    if nested_message not in context_set:
                        context_set[nested_message] = nested_message_name
                        nested_messages += nested_message + '\n'
                else:
                    # 如果定义过了，修改一下名字就行了
                    if value_tuple in message_dict:
                        nested_message_name = message_dict[value_tuple]
                fields += ' ' * indent + f'repeated {u2c(nested_message_name)} {u2c(key)} = {i};\n'
            else:
                fields += ' ' * indent + f'repeated string {u2c(key)} = {i};\n'
        else:
            if isinstance(value, int):
                fields += ' ' * indent + f'optional int32 {u2c(key)} = {i};\n'
            else:
                fields += ' ' * indent + f'optional string {u2c(key)} = {i};\n'
        i += 1

    proto_string = nested_messages + ' ' * indent + f'message {u2c(message_name)} {{\n' + fields + ' ' * indent + '}\n'
    return proto_string
