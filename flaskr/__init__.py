import logging
import os
from logging import handlers

import werkzeug
from flask import Flask, json, render_template, has_request_context, request, g
from flask.logging import default_handler


def create_app(test_config=None):
    ################################################################################################
    # 配置

    # app = Flask(__name__, instance_relative_config=True) 创建 Flask 实例。
    # __name__ 是当前 Python 模块的名称。应用需要知道在哪里设置路径， 使用 __name__ 是一个方便的方法
    # instance_relative_config=True 告诉应用配置文件是相对于 instance folder 的相对路径。
    # 实例文件夹在 flaskr 包的外面，用于存放本地数据（例如配置密钥和数据库），不应当 提交到版本控制系统
    app = Flask(__name__, instance_relative_config=True)

    # app.config.from_mapping() 设置一个应用的 缺省配置：
    # SECRET_KEY 是被 Flask 和扩展用于保证数据安全的。在开发过程中， 为了方便可以设置为 'dev' ，但是在发布的时候应当使用一个随机值来 重载它
    # DATABASE SQLite 数据库文件存放在路径。它位于 Flask 用于存放实例的 app.instance_path 之内
    app.config.from_mapping(
        SECRET_KEY='dev',
        DB_CONNECT='mysql+mysqlconnector://stock:sdasdd@22.125.343.44:3306/stock?charset=utf8',
        DB_POOL_SIZE=10,
        DB_POOL_RECYCLE=3600
    )

    if test_config is None:
        # app.config.from_pyfile() 使用 config.py 中的值来重载缺省配置，如果 config.py 存在的话。 例如，当正式部署的时候，用于设置一个正式的 SECRET_KEY
        # 只有全部是大写字母的变量才会被配置对象所使 用。因此请确保使用大写字母
        app.config.from_pyfile('config.py')  # silent=True
    else:
        # test_config 也会被传递给工厂，并且会替代实例配置。这样可以实现 测试和开发的配置分离，相互独立
        app.config.from_mapping(test_config)

    try:
        # os.makedirs() 可以确保 app.instance_path 存在。 Flask 不会自动 创建实例文件夹，但是必须确保创建这个文件夹
        os.makedirs(app.instance_path)  # app.instance_path的值是flask_tutorial/instance
    except OSError:
        pass

    ################################################################################################
    # 数据库

    from . import db
    db_session_maker = db.create_db_session_maker(app.config['DB_CONNECT'], app.config['DB_POOL_SIZE'], app.config['DB_POOL_RECYCLE'])
    app.db_session_maker = db_session_maker

    from . import db
    db.release_connection_when_request_end(app)

    ################################################################################################
    # 蓝图

    # 使用 app.register_blueprint() 导入并注册 蓝图
    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)  # 与验证蓝图不同，博客蓝图没有 url_prefix 。因此 index 视图会用于 /
    app.add_url_rule('/', endpoint='index')  # 我们使用 app.add_url_rule() 关联端点名称 'index' 和 / URL ，这样 url_for('index') 或 url_for('blog.index') 都会有效，会生成同样的 / URL

    from . import interface_demo
    app.register_blueprint(interface_demo.bp)

    ################################################################################################
    # 错误处理
    # 部分逻辑在 error_util

    # 一个出错处理器是一个返回响应的普通视图函数
    # 通过使用 errorhandler() 装饰函数来注册或者稍后使用 register_error_handler() 来注册(app.register_error_handler(400, handle_bad_request))
    # 当注册时， werkzeug.exceptions.HTTPException 的子类，如 BadRequest ，和它们的 HTTP 代码是可替换的。 （ BadRequest.code == 400 ）
    @app.errorhandler(404)
    def handle_bad_request(e):
        return 'bad request!', 404

    # 因为 Werkzeug 无法识别非标准 HTTP 代码，因此它们不能被注册。替代地，使用适 当的代码定义一个 HTTPException 子类，注册并抛出异常
    class InsufficientStorage(werkzeug.exceptions.HTTPException):
        code = 507
        description = 'Not enough storage space.'

    # 基于 HTTPException 的异常处理器对于把缺省的 HTML 出错页面转换为 JSON 非常有用，
    # 但是这个处理器会触发不由你直接产生的东西，如路由过程中产生的 404 和 405 错误。请仔细制作你的处理器，确保不会丢失关于 HTTP 错误的信息
    # 这里 HTTPException 包含上面的注册的404, 所以若出现404错误, 会优先调用范围小的, 更精确的错误处理器
    @app.errorhandler(werkzeug.exceptions.HTTPException)
    def handle_exception(e):
        """Return JSON instead of HTML for HTTP errors."""
        # start with the correct headers and status code from the error
        response = e.get_response()
        # replace the body with JSON
        response.data = json.dumps({
            "code": e.code,
            "name": e.name,
            "description": e.description,
        })
        response.content_type = "application/json"
        return response

    # 基于 Exception 的异常处理器有助于改变所有异常处理的表现形式，甚至包含 未处理的异常。
    # 但是，与在 Python 使用 except Exception: 类似，这样会捕 获 所有 未处理的异常，包括所有 HTTP 状态码。
    # 因此，在大多数情况下，设定 只针对特定异常的处理器比较安全。
    # 因为 HTTPException 实例是一个合法的 WSGI 响应，你可以直接传递该实例。
    @app.errorhandler(Exception)
    def handle_exception(e):
        # pass through HTTP errors
        if isinstance(e, werkzeug.exceptions.HTTPException):
            return e

        # now you're handling non-HTTP exceptions only
        # return render_template("500_generic.html", e=e), 500
        return str(e), 500

    ################################################################################################
    # 日志

    # 注入请求信息
    # 在蓝图中使用 current_app 打印日志
    class RequestFormatter(logging.Formatter):
        def format(self, record):
            if has_request_context():
                record.url = request.url
                record.remote_addr = request.remote_addr

                record.params_get = request.args
                record.params_form = request.form
                record.params_json = request.get_json()

            else:
                record.url = None
                record.remote_addr = None
                record.params_get = None
                record.params_form = None
                record.params_json = None

            return super().format(record)

    formatter = RequestFormatter(
        '[%(asctime)s] %(remote_addr)s requested %(url)s %(levelname)s in %(module)s: \n'
        'params_get:%(params_get)s\n'
        'params_form:%(params_form)s\n'
        'params_json:%(params_json)s\n'
        '%(message)s'
    )
    file_handler = handlers.RotatingFileHandler(os.path.join(app.instance_path, "../log/flaskr.log"), maxBytes=81920, encoding='utf-8', backupCount=9)
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)

    # app.logger.removeHandler(default_handler)  # 移除的话, 明显的表现是, 在用IDE启动的时候, IDE的启动界面不会打印日志信息了

    #########################################
    # 上传文件
    from . import upload_file_demo
    app.register_blueprint(upload_file_demo.bp)

    from flask_uploads import configure_uploads, patch_request_class

    UPLOADED_PHOTOS_DEST = os.path.join(app.instance_path, "../upload_photos/")  # 文件储存地址设置: UPLOADED_FILES_DEST   默认的配置: UPLOADS_DEFAULT_DEST
    app.config['UPLOADED_PHOTOS_DEST'] = UPLOADED_PHOTOS_DEST  # 文件储存地址
    try:
        os.makedirs(UPLOADED_PHOTOS_DEST)
    except OSError:
        pass

    configure_uploads(app, upload_file_demo.photos)  # 使用configure_uploads()方法注册并完成相应的配置（类似大多数扩展提供的初始化类）
    patch_request_class(app)  # 文件大小限制，默认为16MB

    return app


"""
运行应用

在 Linux and Mac 下：
$ export FLASK_APP=flaskr
$ export FLASK_ENV=development
$ flask run

在 Windows 下，使用 set 代替 export ：
> set FLASK_APP=flaskr
> set FLASK_ENV=development
> flask run

使用PyCharm运行应用
https://blog.miguelgrinberg.com/post/setting-up-a-flask-application-in-pycharm
或者
http://47.92.6.148:6676/notebooks/note/Flask/%E7%A4%BE%E5%8C%BA%E7%89%88PyCharm%E8%BF%90%E8%A1%8CFlask.ipynb
"""
