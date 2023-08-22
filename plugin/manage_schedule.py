import logging
import sqlite3
import os

from plugin.plugin_interface import AbstractPlugin, PluginResult
from jarvis.jarvis import Jarvis
from config import system_config


class ManageSchedulePlugin(AbstractPlugin):
    """
    测试性的插件，效果并不可靠
    """

    def valid(self) -> bool:
        return True

    def __init__(self):
        self._logger = None

    def init(self, logger: logging.Logger):
        self._logger = logger

        # 1. 连接数据库（如果数据库不存在，将会创建新的数据库文件）
        db_file_path = os.path.join(system_config.TEMP_DIR_PATH, "schedule.db")
        conn = sqlite3.connect(db_file_path)

        # 2. 创建游标
        cursor = conn.cursor()

        # 3. 执行SQL语句 - 创建一个名为"users"的表
        create_table_query = '''
            CREATE TABLE IF NOT EXISTS schedule (
                id INTEGER PRIMARY KEY,
                start_time datetime NOT NULL,
                end_time datetime NOT NULL,
                duration TEXT NOT NULL,
                event TEXT NOT NULL
            )
        '''
        cursor.execute(create_table_query)

    def get_name(self):
        return "manage_schedule"

    def get_chinese_name(self):
        return "管理日程"

    def get_description(self):
        return "管理我的日程安排的接口。this function depends on the [get_datetime] function's result. 本接口依赖【获取当前时间】接口的结果。本接口支持对日程安排进行添加、查询、删除操作。"
        # return "管理我的日程安排的接口，当【你知道当前的时间】并且我询问我的日程安排时，你应该调用本接口。\n" \
        #        "当【你知道当前的时间】，并且我让你增加或删除我的某个日程安排时，你也应该调用本接口。\n" \
        #        "注意：如果你不知道当前时间，又认为需要调用本接口时，你应该先调用【获取当前时间接口】，得到当前的时间后，再结合当前时间和我的日程时间，计算出调用本接口的正确的参数值，再调用本接口。\n" \
        #        "注意：你不能在不知道【当前时间】的情况下调用本接口。"

    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "request_type": {
                    "type": "string",
                    "description": "请求的操作类型，你应该在3个枚举值之间选择：‘create’表示添加一条日程；‘delete’表示删除一条日程，‘list’表示查询日程\n"
                                   "当传入create时，你需要传入create_info参数；当传入delete时，你需要传入delete_info参数；当传入list时，你需要传入list_info参数。",
                },
                "create_info": {
                    "type": "object",
                    "properties": {
                        "start_time": {
                            "type": "string",
                            "description": "日程开始时间，格式为【2000-01-01 00:00:00】，你应该传入尽可能准确的时间，你应该使用准确的年、月、日、时、分的数值，不能使用如“今天”、“明天”等代词。正确的示例：2023-07-12 00:00:00。\n"
                                           "如果我说了“明天”等相对的时间点，你应该【先调用查询当前时间接口】获取今天的日期，然后计算我说的相对的时间点具体是哪个日期，然后把具体的日期传给我。以下是几个例子：\n"
                                           "【当前时间】：2023年7月12日\n"
                                           "【我的问题】：我明天中午十二点到一点要出去吃饭\n"
                                           "【start_time】：2023-07-13 12:00:00\n\n"
                                           "【当前时间】：2023年7月28日\n"
                                           "【我的问题】：我后天下午四点到五点要去打羽毛球\n"
                                           "【start_time】：2023-07-30 16:00:00\n\n"
                        },
                        "end_time": {
                            "type": "string",
                            "description": "日程结束时间，格式为【2000-01-01 00:00:00】，你应该传入尽可能准确的时间，你应该使用准确的年、月、日、时、分的数值，不能使用如“今天”、“明天”等代词。正确的示例：2023-07-12 00:00:00。\n"
                                           "end_time和duration这两个参数至少要传一个。以下是几个例子：\n"
                                           "【当前时间】：2023年7月12日\n"
                                           "【我的问题】：我明天中午十二点到一点要出去吃饭\n"
                                           "【end_time】：2023-07-13 13:00:00\n\n"
                                           "【当前时间】：2023年7月28日\n"
                                           "【我的问题】：我后天下午四点到五点要去打羽毛球\n"
                                           "【end_time】：2023-07-30 15:00:00\n\n"
                        },
                        "duration": {
                            "type": "string",
                            "description": "日程的持续时间长度，你应该传入尽可能准确的时间长度，比如：一小时零十分钟。"
                        },
                        "event": {
                            "type": "string",
                            "description": "日程的内容，你应该传入尽可能准确的日程内容信息，尽量不要修改我说的日程内容。"
                        },
                    },
                    "required": ['start_time', 'event'],
                },
                "delete_info": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string",
                            "description": "日程的id。你应该只传入从list功能中获取到的日程id。你不能伪造日程id."
                        },
                    },
                    "required": ['id'],
                },
                "list_info": {
                    "type": "object",
                    "properties": {
                        "filter_start_time": {
                            "type": "string",
                            "description": "筛选条件：日程开始时间晚于传入的时间的日程才会返回。格式为【2023-07-12 00:00:00】\n"
                                           "你应该使用准确的年、月、日、时、分的数值，不能使用如“今天”、“明天”等代词。\n"
                                           "如果你不知道【当前时间】，你应该【先调用查询当前时间接口】获取今天的日期，然后计算我说的相对的时间点具体是哪个日期，然后把具体的日期传给我。以下是几个例子：\n"
                                           "【当前时间】：2023年7月12日\n"
                                           "【我的问题】：我明天有哪些安排\n"
                                           "【filter_start_time】：2023-07-13 00:00:00\n\n"
                                           "【当前时间】：2023年7月28日\n"
                                           "【我的问题】：我后天有哪些安排\n"
                                           "【filter_start_time】：2023-07-30 00:00:00\n\n"
                        },
                        "filter_end_time": {
                            "type": "string",
                            "description": "筛选条件：日程开始时间早于传入的时间的日程才会返回。格式为【2023-07-12 00:00:00】\n"
                                           "你应该使用准确的年、月、日、时、分的数值，不能使用如“今天”、“明天”等代词。\n"
                                           "如果你不知道当前时间，你应该【先调用查询当前时间接口】获取今天的日期，然后计算我说的相对的时间点具体是哪个日期，然后把具体的日期传给我。以下是几个例子：\n"
                                           "【当前时间】：2023年7月12日\n"
                                           "【我的问题】：我明天有哪些安排\n"
                                           "【filter_end_time】：2023-07-13 23:59:59\n\n"
                                           "【当前时间】：2023年7月28日\n"
                                           "【我的问题】：我后天有哪些安排\n"
                                           "【filter_end_time】：2023-07-30 23:59:59\n\n"
                        },
                    },
                    "required": [],
                },
            },
            "required": ["request"],
        }

    def run(self, jarvis: Jarvis, args: dict) -> PluginResult:
        action = args.get("request_type")

        db_file_path = os.path.join(system_config.TEMP_DIR_PATH, "schedule.db")
        conn = sqlite3.connect(db_file_path)

        # 2. 创建游标
        cursor = conn.cursor()
        if action == "list":
            select_query = '''
                SELECT * FROM schedule where 1=1
            '''
            if args.get("list_info").get("filter_start_time") is not None:
                select_query += " and start_time > '{}'".format(args.get("list_info").get("filter_start_time"))
            if args.get("list_info").get("filter_end_time") is not None:
                select_query += " and start_time < '{}'".format(args.get("list_info").get("filter_end_time"))

            try:
                cursor.execute(select_query)
                rows = cursor.fetchall()
            except Exception as e:
                self._logger.error("execute sql failed, sql: {}, exception: {}".format(select_query, e))
                return PluginResult.new(result="查询日程失败", need_call_brain=True)
            if len(rows) == 0:
                return PluginResult.new(result="没有日程安排", need_call_brain=True)

            result = "我接下来的日程安排如下：\n"
            for row in rows:
                result += "id：{}, 开始时间：{}, 结束时间：{}, 时长：{}, 日程内容：{}\n".format(row[0], row[1], row[2],
                                                                                           row[3], row[4])
            result += "你应该只回答我返回的这些日程内容，不能擅自添加任何不存在的日程安排。\n" \
                      "你应该根据今天的日期和我问的日期来决定告诉我哪些日程，不要将我问的日期之外的日程告诉我。\n" \
                      "例如：如果我问明天的日程安排，你不能将今天的日程告诉我。"
            return PluginResult.new(result=result, need_call_brain=True)

        elif action == "create":
            insert_query = '''
                INSERT INTO schedule (start_time, end_time, duration, event) VALUES (?, ?, ?, ?)
            '''
            create_info = args.get("create_info")
            schedule_data = (create_info.get("start_time"),
                             create_info.get("end_time") if create_info.get("end_time") is not None else "",
                             create_info.get("duration") if create_info.get("duration") is not None else "",
                             create_info.get("event"))

            try:
                cursor.execute(insert_query, schedule_data)
                # 提交事务
                conn.commit()
            except Exception as e:
                self._logger.error("execute sql failed, sql: {}, exception: {}".format(insert_query, e))
                return PluginResult.new(result="添加日程失败", need_call_brain=True)
            return PluginResult.new(result="添加日程成功", need_call_brain=True)
        elif action == "delete":
            delete_query = '''
                DELETE FROM schedule where id = ?
            '''
            data = (args.get("delete_info").get("id"))

            try:
                cursor.execute(delete_query, data)
                # 提交事务
                conn.commit()
            except Exception as e:
                self._logger.error("execute sql failed, sql: {}, exception: {}".format(delete_query, e))
                return PluginResult.new(result="删除日程失败", need_call_brain=True)
            return PluginResult.new(result="删除日程成功", need_call_brain=True)
