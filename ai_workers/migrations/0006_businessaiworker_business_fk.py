from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def map_user_business_to_business_model(apps, schema_editor):
    Business = apps.get_model('business', 'Business')
    BusinessAIWorker = apps.get_model('ai_workers', 'BusinessAIWorker')

    for worker in BusinessAIWorker.objects.all().iterator():
        business = Business.objects.filter(owner_id=worker.legacy_business_user_id).first()
        if business:
            worker.business = business
            worker.save(update_fields=['business'])


def reverse_map_business_to_user(apps, schema_editor):
    BusinessAIWorker = apps.get_model('ai_workers', 'BusinessAIWorker')
    for worker in BusinessAIWorker.objects.select_related('business').all().iterator():
        if worker.business_id and worker.business.owner_id:
            worker.legacy_business_user_id = worker.business.owner_id
            worker.save(update_fields=['legacy_business_user'])


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0008_alter_task_budget'),
        ('ai_workers', '0005_financialreport_lease_tenant_paymentreminder_payment_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameField(
            model_name='businessaiworker',
            old_name='business',
            new_name='legacy_business_user',
        ),
        migrations.AddField(
            model_name='businessaiworker',
            name='business',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ai_workers', to='business.business'),
        ),
        migrations.RunPython(map_user_business_to_business_model, reverse_map_business_to_user),
        migrations.AlterField(
            model_name='businessaiworker',
            name='business',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ai_workers', to='business.business'),
        ),
        migrations.RemoveField(
            model_name='businessaiworker',
            name='legacy_business_user',
        ),
    ]
