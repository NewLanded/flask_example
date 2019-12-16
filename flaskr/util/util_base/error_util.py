# 实现 API 异常
# ，实现你自己 的异常类型并为之安装一个错误处理器


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload  # 通过 payload 参数，可以以字典方式 提供一些额外的负载

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


# 使用方法为
"""
@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
"""
