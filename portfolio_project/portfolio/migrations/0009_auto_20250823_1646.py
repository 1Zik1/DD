from django.db import migrations

def remove_null_files(apps, schema_editor):
    File = apps.get_model('portfolio', 'File')
    # Удаляем все записи, где content_type или object_id равны NULL
    File.objects.filter(content_type__isnull=True).delete()
    File.objects.filter(object_id__isnull=True).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0006_merge_20250823_1554'),  # Укажите вашу последнюю миграцию
    ]

    operations = [
        migrations.RunPython(remove_null_files, migrations.RunPython.noop),
    ]