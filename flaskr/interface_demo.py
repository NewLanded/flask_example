from flask import Blueprint, request, jsonify, current_app

from flaskr.util.util_data.basic_info import BasicInfo

bp = Blueprint('interface_map', __name__)  # 如果不写url_prefix就是在 / 下


@bp.route('/hello')
def hello():
    current_app.logger.info('hello world test log')

    return "hello world"


@bp.route('/hello/<name>')
def hello_name(name):
    return name


@bp.route('/hello/post_name', methods=('POST',))
def hello_name_post():
    name = request.form['name']
    return name


# 返回json示例
@bp.route('/json/auth', methods=('POST',))
def auth():
    json_data = request.get_json()
    email = json_data['email']
    password = json_data['password']

    return jsonify(token=email + password)


# 测试连接数据库
@bp.route('/db_test')
def db_test():
    result = BasicInfo().get_one_test_row()
    result = jsonify(result)

    return result


# 测试流内容
# 有时候你会需要把大量数据传送到客户端，不在内存中保存这些数据
# 注意，当你生成流内容时，请求情境已经在函数执行时消失了。 stream_with_context 为你提 供了一点帮助，让你可以在生成器运行期间保持请求情境
from flask import stream_with_context, Response


@bp.route('/stream')
def streamed_response():
    def generate():
        yield 'Hello '
        yield request.args.get('name', "123")  # 默认返回None的话会报错
        yield '!'

    return Response(stream_with_context(generate()))
