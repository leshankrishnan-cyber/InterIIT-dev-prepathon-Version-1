import subprocess
import sys

def run(command):
    print(f"$ {command}")
    result = subprocess.run(command, shell=True, text=True)
    return result.returncode

def break_database_host():
    run(
        "kubectl set env deployment/api "
        "-n rca DB_HOST=invalid-database"
    )

def restore_database_host():
    run(
        "kubectl set env deployment/api "
        "-n rca DB_HOST=postgres-service"
    )

if __name__ == "__main__":
    action = sys.argv[1]

    if action == "break":
        break_database_host()
    elif action == "restore":
        restore_database_host()
