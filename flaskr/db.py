from flask import current_app, g
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def create_db_session_maker(DB_CONNECT, DB_POOL_SIZE, DB_POOL_RECYCLE):
    engine = create_engine(DB_CONNECT, echo=False, pool_size=DB_POOL_SIZE, pool_recycle=DB_POOL_RECYCLE)
    db_session_maker = sessionmaker(bind=engine)
    return db_session_maker


def get_db():
    # g 是一个特殊对象，独立于每一个请求。在处理请求过程中，它可以用于储存 可能多个函数都会用到的数据。
    # 把连接储存于其中，可以多次使用，而不用在同一个 请求中每次调用 get_db 时都创建一个新的连接
    if 'db' not in g:
        # current_app 是另一个特殊对象，该对象指向处理请求的 Flask 应用
        g.db = current_app.db_session_maker()

    return g.db


# close_db 通过检查 g.db 来确定连接是否已经建立。如果连接已建立，那么 就关闭连接。以后会在应用工厂中告诉应用 close_db 函数，这样每次请求后就会 调用它
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


# close_db 和 init_db_command 函数需要在应用实例中注册，否则无法使用。 然而，既然我们使用了工厂函数，那么在写函数的时候应用实例还无法使用。
# 代替地， 我们写一个函数，把应用作为参数，在函数中进行注册
def release_connection_when_request_end(app):
    # app.teardown_appcontext() 告诉 Flask 在返回响应后进行清理的时候调用此函数
    app.teardown_appcontext(close_db)
