"""
pytest项目放置固件的文件

固件（Fixture）是一些函数，pytest 会在执行测试函数之前（或之后）加载运行它们

在复杂的项目中，可以在不同的目录层级定义 conftest.py，其作用域为其所在的目录和子目录

不要自己显式调用 conftest.py，pytest 会自动调用，可以把 conftest 当做插件来理解
"""

import os

import pytest
from flask import g

from config import TEST_DB_CONNECT
from flaskr import create_app
from flaskr.db import get_db

with open(os.path.join(os.path.dirname(__file__), "data.sql"), "rb") as f:
    _data_sql = f.read().decode("utf8")


# 现在使用 pytest.fixture 有一个问题
# 当你运行多个测试的时候, 比如运行两次 client.get("/hello"),  这时 current_app.logger.info('hello world test log') 会打印出三次访问日志 (使用 print 或者 向一个文件中写入则不会出现这个问题)
# scope="session" 是说不让每一个测试都调用  pytest.fixture,  只调用一次, 即只创建一个服务, 这样可以暂时覆盖这个问题
@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # create the app with common test config
    app = create_app({"DB_CONNECT": TEST_DB_CONNECT})

    # create the database and load test data
    with app.app_context():
        get_db()
        aa = g.db.execute(_data_sql).fetchone()  # 用来测试, 实际使用的时候应该是清理或初始化需要的数据

    yield app

    # 可以在这里做一些清理工作
    print("end ever test doing sonething")


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


# 这是用来验证需要登录的接口
class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username="test", password="test"):
        return self._client.post(
            "/auth/login", data={"username": username, "password": password}
        )

    def logout(self):
        return self._client.get("/auth/logout")


@pytest.fixture
def auth(client):
    return AuthActions(client)
