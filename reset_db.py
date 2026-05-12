import os
import django
from django.core.management import call_command

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

def reset_db():
    print("Deleting old DBs...")
    files_in_dir = os.listdir(".")
    for file in files_in_dir:
        if file.endswith(".sqlite3"):
            try:
                os.remove(file)
                print(f"Successfully delete {file}")
            except OSError as e:
                print(f"Couldn't delete {file}: {e}")

    print("Running migrations...")
    call_command("migrate", "--database=default")
    call_command("migrate", "--database=vulnerable_db")

    print("Loading data...")
    call_command("loaddata", "--database=default", "secure-sample")
    call_command("loaddata", "--database=vulnerable_db", "vulnerable-sample")

    print("Database reset complete!")


if __name__ == "__main__":
    reset_db()