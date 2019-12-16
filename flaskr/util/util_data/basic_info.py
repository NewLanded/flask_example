from flaskr.db import get_db
from flaskr.util.util_base.db_util import get_multi_data


class BasicInfo:
    def __init__(self):
        self._session = get_db()

    def get_one_test_row(self):
        sql = """
        select * from s_info where code='000001'
        """
        args = {}
        result = get_multi_data(self._session, sql, args)
        return result
