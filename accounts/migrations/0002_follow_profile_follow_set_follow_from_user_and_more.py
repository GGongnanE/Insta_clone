# Generated by Django 4.0.4 on 2022-05-30 06:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Follow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='profile',
            name='follow_set',
            field=models.ManyToManyField(blank=True, through='accounts.Follow', to='accounts.profile'),
        ),
        migrations.AddField(
            model_name='follow',
            name='from_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='follow_user', to='accounts.profile'),
        ),
        migrations.AddField(
            model_name='follow',
            name='to_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='follower_user', to='accounts.profile'),
        ),
        migrations.AlterUniqueTogether(
            name='follow',
            unique_together={('from_user', 'to_user')},
        ),
    ]
