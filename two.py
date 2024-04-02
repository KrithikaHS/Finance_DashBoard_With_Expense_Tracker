import sqlite3

DATABASE = "expenses.db"

def delete_expense(expense_id):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("DELETE FROM expenses WHERE ID = ?", (expense_id,))

    conn.commit()

    conn.close()
delete_expense(4)#replace 4 with the ID which u want to delete