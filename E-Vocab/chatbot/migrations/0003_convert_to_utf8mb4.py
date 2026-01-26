# Generated manually - Convert table to utf8mb4

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0002_rename_chatbot_cha_user_id_timestamp_idx_chatbot_cha_user_id_ac2c89_idx'),
    ]

    operations = [
        # Convert table và tất cả text columns sang utf8mb4
        migrations.RunSQL(
            sql="""
                ALTER TABLE chatbot_chatmessage CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
                ALTER TABLE chatbot_chatmessage MODIFY content TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
                ALTER TABLE chatbot_chatmessage MODIFY message_type VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
                ALTER TABLE chatbot_chatmessage MODIFY audio_url VARCHAR(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
                ALTER TABLE chatbot_chatmessage MODIFY word VARCHAR(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
                ALTER TABLE chatbot_chatmessage MODIFY phonetic VARCHAR(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]

