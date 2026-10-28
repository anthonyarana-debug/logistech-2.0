from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="ThrottleWindow",
            fields=[
                ("key", models.CharField(max_length=64, primary_key=True, serialize=False)),
                ("history", models.JSONField(default=list)),
                ("expires_at", models.DateTimeField(db_index=True)),
            ],
        ),
    ]
