from django.db import migrations
import os

def create_views(apps, schema_editor):
    # Исправленный путь: поднимаемся на уровень выше, затем в папку sql
    file_path = os.path.join(os.path.dirname(__file__), '../sql/0002_create_views.sql')
    with open(file_path, 'r') as f:
        sql = f.read()
        schema_editor.execute(sql)

def drop_views(apps, schema_editor):
    schema_editor.execute("""
        DROP VIEW IF EXISTS teacher_experience;
        DROP VIEW IF EXISTS teaching_quality;
        DROP VIEW IF EXISTS teacher_portfolio;
    """)

class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0003_teacher_user'),
    ]

    operations = [
        migrations.RunPython(create_views, drop_views),
    ]