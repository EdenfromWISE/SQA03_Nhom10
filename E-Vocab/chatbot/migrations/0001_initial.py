# Generated manually

from django.conf import settings
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('user', 'User'), ('assistant', 'Assistant')], max_length=20)),
                ('content', models.TextField()),
                ('timestamp', models.BigIntegerField()),
                ('message_type', models.CharField(blank=True, max_length=50, null=True)),
                ('audio_url', models.CharField(blank=True, max_length=500, null=True)),
                ('word', models.CharField(blank=True, max_length=200, null=True)),
                ('phonetic', models.CharField(blank=True, max_length=200, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_messages', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['timestamp'],
            },
        ),
        migrations.AddIndex(
            model_name='chatmessage',
            index=models.Index(fields=['user', 'timestamp'], name='chatbot_cha_user_id_timestamp_idx'),
        ),
        # Set charset utf8mb4 để hỗ trợ emoji và ký tự đặc biệt
        migrations.RunSQL(
            sql="ALTER TABLE chatbot_chatmessage CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]

