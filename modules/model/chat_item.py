class ChatItem:
    def __init__(self):
        self.role = None
        self.content = None
        self.function_call = None
        # 函数调用的结果中使用该参数传递函数名
        self.name = None

    def to_dict(self):
        """将 ChatItem 转换为可序列化的字典"""
        return {
            "role": self.role,
            "content": self.content,
            "function_call": self.function_call,
            "name": self.name,
        }

    @staticmethod
    def new(role, content, function_call=None, name=None):
        item = ChatItem()
        item.role = role
        item.content = content
        item.function_call = function_call
        item.name = name
        return item
