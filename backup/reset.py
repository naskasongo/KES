import os
import subprocess
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wantashi.settings')
django.setup()


def complete_reset():
    print("🔄 COMPLETE DATABASE RESET")
    print("=" * 50)

    # 1. RECREATE POSTGRESQL DATABASE
    print("1. Recreating PostgreSQL database...")
    try:
        import psycopg2
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password='Nas08@kas05',
            host='localhost'
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Force disconnect all users
        cursor.execute("""
                       SELECT pg_terminate_backend(pg_stat_activity.pid)
                       FROM pg_stat_activity
                       WHERE pg_stat_activity.datname = 'schooldb'
                         AND pid <> pg_backend_pid();
                       """)

        cursor.execute("DROP DATABASE IF EXISTS schooldb")
        cursor.execute("CREATE DATABASE schooldb OWNER postgres")
        cursor.close()
        conn.close()
        print("   ✅ Database recreated")
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return False

    # 2. DELETE ALL MIGRATION FILES
    print("2. Cleaning migration files...")
    migration_files_deleted = 0
    for root, dirs, files in os.walk('..'):
        if 'migrations' in dirs:
            mig_dir = os.path.join(root, 'migrations')
            for file in os.listdir(mig_dir):
                if file.startswith('0') and (file.endswith('.py') or file.endswith('.pyc')):
                    os.remove(os.path.join(mig_dir, file))
                    migration_files_deleted += 1
    print(f"   ✅ Deleted {migration_files_deleted} migration files")

    # 3. DELETE MIGRATION CACHE
    print("3. Cleaning migration cache...")
    try:
        subprocess.run(['python', 'manage.py', 'migrate', '--run-syncdb'],
                       capture_output=True, text=True, timeout=30)
    except:
        pass  # Ignore errors here

    # 4. RECREATE MIGRATIONS
    print("4. Creating new migrations...")
    try:
        result = subprocess.run(['python', 'manage.py', 'makemigrations'],
                                capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print("   ✅ Migrations created successfully")
        else:
            print(f"   ⚠️ Makemigrations output: {result.stderr}")
    except Exception as e:
        print(f"   ❌ Makemigrations failed: {e}")
        return False

    # 5. APPLY MIGRATIONS
    print("5. Applying migrations...")
    try:
        result = subprocess.run(['python', 'manage.py', 'migrate'],
                                capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            print("   ✅ All migrations applied successfully")
        else:
            print(f"   ⚠️ Migrate output: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ Migrate failed: {e}")
        return False

    print("=" * 50)
    print("🎉 COMPLETE RESET SUCCESSFUL!")
    print("You can now use pgloader to migrate your data")
    return True


if __name__ == "__main__":
    complete_reset()