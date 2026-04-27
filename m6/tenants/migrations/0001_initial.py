import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Tenant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('plan', models.CharField(
                    choices=[('free', 'Free'), ('pro', 'Pro'), ('enterprise', 'Enterprise')],
                    default='free',
                    max_length=20,
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
                ('max_users', models.IntegerField(default=5)),
                ('max_projects', models.IntegerField(default=3)),
                ('owner', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='owned_tenants',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'ordering': ['name'],
            },
        ),
    ]
