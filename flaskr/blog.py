from flask import Blueprint, redirect, url_for

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required  # 装饰器, 调用这个接口需要先登录
def delete(id):
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))
