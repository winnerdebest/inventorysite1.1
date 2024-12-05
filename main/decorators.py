from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

def role_required(group_name):
    def decorator(view_func):
        @login_required
        def wrapped_view(request, *args, **kwargs):
            # Check if the user belongs to the required group
            if request.user.groups.filter(name=group_name).exists():
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("You do not have access to this view.")
        return wrapped_view
    return decorator
