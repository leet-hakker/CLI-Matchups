import sqlite3

# Checks if a value exists in a column of a table
# https://stackoverflow.com/a/39283198/9899381
def has_value(location, table, column, value):
    conn = sqlite3.connect(location)
    c = conn.cursor()
    query = "SELECT 1 from {} WHERE {} = ? LIMIT 1".format(table, column)
    return c.execute(query, (value,)).fetchone() is not None


def check_if_user_exists(location, user_name):
    return has_value(location, "users", "user_name", user_name)
