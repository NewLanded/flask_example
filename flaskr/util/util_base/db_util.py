def get_multi_data(session, sql, args=None):
    try:
        if args is None:
            result = session.execute(sql).fetchall()
        else:
            result = session.execute(sql, args).fetchall()
    except Exception as e:
        raise e

    result = [list(i) for i in result] if result else result

    return result


def get_single_column(session, sql, args=None):
    result = get_multi_data(session, sql, args)
    result = [i[0] for i in result]
    return result


def get_single_row(session, sql, args=None):
    try:
        if args is None:
            result = session.execute(sql).first()
        else:
            result = session.execute(sql, args).first()
    except Exception as e:
        raise e

    result = list(result) if result else result

    return result


def get_single_value(session, sql, args=None):
    result = get_multi_data(session, sql, args)
    result = None if not result else result[0][0]
    return result


def get_boolean_value(session, sql, args=None):
    result = get_multi_data(session, sql, args)
    if len(result) > 0 and result[0][0] == 1:
        return True
    else:
        return False


def update_data(session, sql, args=None):
    try:
        if args is None:
            session.execute(sql)
        else:
            session.execute(sql, args)
        session.commit()
    except Exception as e:
        raise e
