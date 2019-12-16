"""
应用调度是在 WSGI 层面组合多个 Flask 应用的过程。可以组合多个 Flask 应用， 也可以组合 Flask 应用和其他 WSGI 应用。
通过这种组合，如果有必要的话，甚至 可以在同一个解释器中一边运行 Django ，一边运行 Flask 。这种组合的好处取决 于应用内部是如何工作的。

应用调度与 模块化 的最大不同在于应用调度中的 每个应用是完全独立的，它们以各自的配置运行，并在 WSGI 层面被调度

下面所有的技术说明和举例都归结于一个可以运行于任何 WSGI 服务器的 application 对象, 对于开发环境， Werkzeug 提供了一个内建开发服务器，它使用 werkzeug.serving.run_simple() 来运行:

"""

"""
# 简单使用 werkzeug.serving.run_simple() 启动
from werkzeug.serving import run_simple

from flaskr import create_app

if __name__ == '__main__':
    app = create_app()
    run_simple('localhost', 5000, app,
               use_reloader=True, use_debugger=True, use_evalex=True)
"""

# 组合应用
# 如果你想在同一个 Python 解释器中运行多个独立的应用，那么你可以使用 werkzeug.wsgi.DispatcherMiddleware 。
# 其原理是：每个独立的 Flask 应用都是一个合法的 WSGI 应用，它们通过调度中间件组合为一个基于前缀调度的大应用
# 假设你的主应用运行于 / ，后台接口位于 /backend


if __name__ == '__main__':
    from werkzeug.serving import run_simple

    from werkzeug.wsgi import DispatcherMiddleware
    from flaskr import create_app as frontend
    from flaskr import create_app as backend

    app = DispatcherMiddleware(
        frontend(),
        {'/backend': backend()}
    )

    run_simple('localhost', 5000, app,
               use_reloader=True, use_debugger=True, use_evalex=True)
