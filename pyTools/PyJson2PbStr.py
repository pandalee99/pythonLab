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


def to_tuple_sorted(x):
    # 将字典或列表转换为元组，以便可以将其用作字典的键
    if isinstance(x, dict):
        return tuple((k, to_tuple_sorted(v)) for k, v in sorted(x.items()))
    elif isinstance(x, list):
        return tuple(to_tuple_sorted(v) for v in x)
    else:
        return x


def dict_to_proto(data, message_name="Example", indent=0, message_dict=None, root=True, root_messages=None):
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
                nested_message = dict_to_proto(value, message_name=nested_message_name, indent=indent + 2,
                                               message_dict=message_dict, root=False, root_messages=root_messages)
                root_messages.append(
                    ' ' * (indent + 2) + f'message {nested_message_name} {{\n' + nested_message + ' ' * (
                            indent + 2) + '}\n')
            fields += ' ' * (indent + 2) + f'optional {nested_message_name} {key} = {i};\n'
        elif isinstance(value, list):
            # 如果值是列表，那么需要为它创建一个新的消息类型
            if all(isinstance(item, dict) for item in value):
                value_tuple = to_tuple_sorted(value[0])
                nested_message_name = key.capitalize()
                if value_tuple not in message_dict:
                    message_dict[value_tuple] = nested_message_name
                    nested_message = dict_to_proto(value[0], message_name=nested_message_name, indent=indent + 2,
                                                   message_dict=message_dict, root=False, root_messages=root_messages)
                    root_messages.append(
                        ' ' * (indent + 2) + f'message {nested_message_name} {{\n' + nested_message + ' ' * (
                                indent + 2) + '}\n')
                fields += ' ' * (indent + 2) + f'repeated {nested_message_name} {key} = {i};\n'
            else:
                fields += ' ' * (indent + 2) + f'repeated string {key} = {i};\n'
        else:
            # 如果值是基本类型，那么直接添加字段
            if isinstance(value, int):
                fields += ' ' * (indent + 2) + f'optional int32 {key} = {i};\n'
            else:
                fields += ' ' * (indent + 2) + f'optional string {key} = {i};\n'
        i += 1

    if root:
        # 如果是根消息，那么需要添加所有的嵌套消息和字段
        proto_string = ' ' * indent + f'message {message_name} {{\n' + ''.join(
            root_messages) + fields + ' ' * indent + '}\n'
    else:
        # 如果不是根消息，那么只需要添加字段
        proto_string = fields
    return proto_string


print(dict_to_proto(resp_dict))
