from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('portfolio', '0006_merge_20250823_1554'),  # Укажите последнюю существующую миграцию
    ]

    operations = [
        migrations.RunSQL(
            open('portfolio/sql/0002_create_views.sql').read()
        )
    ]