"""Encrypt bank_account and ifsc_code fields on InsuranceClaim."""
from django.db import migrations
import config.encryption


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0002_costentry_finance_cos_user_id_9f4912_idx_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='insuranceclaim',
            name='bank_account',
            field=config.encryption.EncryptedCharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='insuranceclaim',
            name='ifsc_code',
            field=config.encryption.EncryptedCharField(blank=True, max_length=200),
        ),
    ]
