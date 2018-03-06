# todo: not sure what they exactly want, 'django.db.backends' would be nice too
from datastore.models import DataLog


def save_log(sender, **kwargs):
    """Call back to log save operations on Data model"""
    instance = kwargs['instance']
    if kwargs['created']:
        l_type = 'created'
    else:
        l_type = 'updated'
    # todo raw sql query check
    DataLog.objects.create(
        slot_name=instance.slot_name,
        service_user=instance.service_user_id,
        json_data=instance.json_data,
        type=l_type
    )


def delete_log(sender, **kwargs):
    """Call back to log save operations on Data model"""
    instance = kwargs['instance']
    # todo raw sql query check
    DataLog.objects.create(
        slot_name=instance.slot_name,
        service_user=instance.service_user_id,
        json_data=instance.json_data,
        type='deleted'
    )
