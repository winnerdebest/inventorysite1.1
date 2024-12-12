from django.db.models.signals import post_migrate
from django.contrib.auth.models import Group
from django.dispatch import receiver

@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    # List of group names
    default_groups = [
        "General Manager",
        "Coordinators",
        "Internal Control",
        "Inventory Manager",
        "Procurement",
        "Supervisor",
    ]

    for group_name in default_groups:
        # Create group if it doesn't exist
        Group.objects.get_or_create(name=group_name)
