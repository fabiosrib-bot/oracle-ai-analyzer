import tkinter as tk
from tkinter import messagebox
import oracledb

oracledb.init_oracle_client(lib_dir=r"C:\Oracle\ora112\instantclient")

def analyze_database(conn):

    cursor = conn.cursor()
    report = ""

    report += "===== ORACLE DATABASE HEALTH CHECK =====\n\n"

    # INSTANCE
    cursor.execute("select instance_name, host_name, version from v$instance")
    instance = cursor.fetchone()

    report += f"Instance: {instance[0]}\n"
    report += f"Host: {instance[1]}\n"
    report += f"Version: {instance[2]}\n\n"

    # DATABASE ROLE
    cursor.execute("select name, database_role, open_mode from v$database")
    db = cursor.fetchone()

    report += f"Database: {db[0]}\n"
    report += f"Role: {db[1]}\n"
    report += f"Open Mode: {db[2]}\n\n"

    # RAC NODES
    report += "===== RAC NODES =====\n"

    cursor.execute("select inst_id, instance_name, host_name from gv$instance")

    for row in cursor:
        report += f"Node {row[0]} : {row[1]} ({row[2]})\n"

    report += "\n"

    # ACTIVE SESSIONS
    cursor.execute("""
    select count(*)
    from gv$session
    where status='ACTIVE'
    """)

    active_sessions = cursor.fetchone()[0]

    report += f"Active Sessions: {active_sessions}\n\n"

    # BLOCKING SESSIONS
    cursor.execute("""
    select count(*)
    from gv$session
    where blocking_session is not null
    """)

    blocking = cursor.fetchone()[0]

    report += f"Blocking Sessions: {blocking}\n\n"

    # TABLESPACE USAGE
    report += "===== TABLESPACE USAGE =====\n"

    cursor.execute("""
    select tablespace_name, round(used_percent,2)
    from dba_tablespace_usage_metrics
    order by used_percent desc
    fetch first 10 rows only
    """)

    for row in cursor:
        report += f"{row[0]} : {row[1]}%\n"

    report += "\n"

    return report


def connect_db():

    host = entry_host.get()
    port = entry_port.get()
    service = entry_service.get()
    user = entry_user.get()
    password = entry_password.get()

    dsn = f"{host}:{port}/{service}"

    try:

        conn = oracledb.connect(
            user=user,
            password=password,
            dsn=dsn,
        )

        report = analyze_database(conn)

        text_output.delete(1.0, tk.END)
        text_output.insert(tk.END, report)

    except Exception as e:

        messagebox.showerror("Connection Error", str(e))


root = tk.Tk()

root.title("Oracle AI DBA Assistant")
root.geometry("650x500")


tk.Label(root, text="Hostname").grid(row=0)
tk.Label(root, text="Port").grid(row=1)
tk.Label(root, text="Service").grid(row=2)
tk.Label(root, text="User").grid(row=3)
tk.Label(root, text="Password").grid(row=4)

entry_host = tk.Entry(root)
entry_port = tk.Entry(root)
entry_service = tk.Entry(root)
entry_user = tk.Entry(root)
entry_password = tk.Entry(root, show="*")

entry_host.grid(row=0, column=1)
entry_port.grid(row=1, column=1)
entry_service.grid(row=2, column=1)
entry_user.grid(row=3, column=1)
entry_password.grid(row=4, column=1)

entry_port.insert(0, "1521")

tk.Button(root, text="Analyze Database", command=connect_db).grid(row=5, column=1)


text_output = tk.Text(root, height=20, width=80)
text_output.grid(row=6, columnspan=2)


root.mainloop()
