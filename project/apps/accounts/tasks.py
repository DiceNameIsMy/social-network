from django.contrib.contenttypes.models import ContentType

from celery import shared_task

from .models import CustomUser, Notification


@shared_task
def create_notification(
    user: CustomUser,
    notification_type: int, 
    message: str, 
    obj
) -> int:
    """
    Create notification and send it to online users
    """
    notification = Notification.objects.create(**{
        'user': user,
        'type': notification_type,
        'message': message,
        'content_type': ContentType.objects.get_for_model(obj),
        'object_id': obj.pk
    })
    # TODO: send notification to online users
    return notification.id