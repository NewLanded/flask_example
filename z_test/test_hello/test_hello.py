import pytest
from flask import g

from flaskr.db import get_db


def test_hello_1(app, client):
    # test that viewing the page renders without template errors
    assert client.get("/hello").status_code == 200


# def test_hello_1_2(app, client):
#     # test that viewing the page renders without template errors
#     assert client.get("/hello").status_code == 200

def test_hello_2(client, app):
    # test that successful registration redirects to the login page
    response = client.get("/hello")
    print(response.data)


def test_hello_3(client, app):
    # test that the user was inserted into the database
    with app.app_context():
        get_db()
        print(g.db.execute("select * from s_info where code='000001'").fetchone())


# 参数化测试, 这里定义了三个参数, 会去发三次请求
@pytest.mark.parametrize(
    ("name",),
    (
            ("name_1",),
            ("name_2",),
            ("name_3",),
    ),
)
def test_hello_name(client, name):
    response = client.get("/hello/{0}".format(name))
    print(response.data)


@pytest.mark.parametrize(
    ("name",),
    (
            ("post_name_1",),
            ("post_name_2",),
            ("post_name_3",),
    ),
)
def test_hello_post_name(client, name):
    response = client.post(
        "/hello/post_name", data={"name": name}
    )
    print(response.data)


# 这个示例用来测试json
def test_json_interface(client):
    response = client.post('/json/auth', json={
        'email': 'flask@example.com', 'password': 'secret'
    })
    json_data = response.get_json()
    print(json_data)


"""
# 这个示例用来测试需要登录后调用的接口
def test_create(client, auth, app):
    auth.login()
    assert client.get("/create").status_code == 200
    client.post("/create", data={"title": "created", "body": ""})

    with app.app_context():
        db = get_db()
        count = db.execute("SELECT COUNT(id) FROM post").fetchone()[0]
        assert count == 2
"""

"""
注意，在测试请求环境中 before_request() 和 after_request() 不会被自动调用。
但是当调试请求环境离开 with 块时会执行 teardown_request() 函数。
如果需要 before_request() 函数和正常情况下一样被调用，那么需要自 己调用 preprocess_request()

app = flask.Flask(__name__)

with app.test_request_context('/?name=Peter'):
    app.preprocess_request()
    ...
    
在这函数中可以打开数据库连接或者根据应用需要打开其他类似东西。


如果想调用 after_request() 函数，那么必须调用 process_response() ，并把响应对象传递给它:

app = flask.Flask(__name__)

with app.test_request_context('/?name=Peter'):
    resp = Response('...')
    resp = app.process_response(resp)
    ...
"""

if __name__ == '__main__':
    import os

    pytest.main([os.path.join(os.path.curdir, __file__), "-s", "--tb=short", "--html=./report.html"])
