import sqlite3


class db_cursor(object):
    def __init__(self, db_path):
        self.db_path = db_path

    def __enter__(self):
        self.db_conn = sqlite3.connect(self.db_path)
        cursor = self.db_conn.cursor()
        return cursor

    def __exit__(self, type, value, traceback):
        self.db_conn.commit()
        self.db_conn.close()


def db_insert(db_path, table, fields):
    columns = ", ".join(fields.keys())
    placeholders = ("?, " * len(fields))[:-2]
    field_values = _decode_utf8_values(fields.values())
    with db_cursor(db_path) as cursor:
        try:
            cursor.execute(
                "insert into {0}({1}) values ({2})".format(
                    table, columns, placeholders
                ),
                field_values
            )
        except sqlite3.IntegrityError:
            print columns
            print field_values
            raise
        inserted_id = cursor.lastrowid
    return inserted_id


def db_update(db_path, table, updated_fields, row):
    """Update `table` with the values given in the dict `values` on the
       condition given with the `row` tuple.
    """
    columns = "=?, ".join(updated_fields.keys()) + "=?"
    field_values = _decode_utf8_values(updated_fields.values())
    condition_field = "{0}=?".format(row[0])
    condition_value = (row[1], )
    with db_cursor(db_path) as cursor:
        query = "UPDATE {0} SET {1} WHERE {2}".format(table, columns,
                                                      condition_field)
        cursor.execute(query, field_values + condition_value)


def db_delete(db_path, table, field, value):
    with db_cursor(db_path) as cursor:
        cursor.execute("delete from {0} where {1}=?".format(table, field),
                       (value,))


def db_select(db_path, table, fields=None, condition=None):
    if fields:
        columns = ", ".join(fields)
    else:
        columns = "*"
    with db_cursor(db_path) as cursor:
        if condition:
            assert len(condition) == 2
            cursor.execute(
                "SELECT {0} FROM {1} where {2}=?".format(
                    columns, table, condition[0]
                ), (condition[1], )
            )
        else:
            cursor.execute("SELECT {0} FROM {1}".format(columns, table))
        rows = cursor.fetchall()
        column_names = [column[0] for column in cursor.description]
    results = []
    for row in rows:
        row_data = {}
        for index, column in enumerate(column_names):
            row_data[column] = row[index]
        results.append(row_data)
    return results


def _decode_utf8_values(values_list):
    """Return a tuple of values with UTF-8 string values being decoded."""
    i = 0
    for v in values_list:
        if type(v) is str:
            values_list[i] = v.decode('UTF-8')
        i += 1
    return tuple(values_list)


def add_field(db_path, tablename, field):
    query = "ALTER TABLE %s ADD COLUMN %s %s" % (
        tablename, field['name'], field['type']
    )
    with db_cursor(db_path) as cursor:
        cursor.execute(query)
