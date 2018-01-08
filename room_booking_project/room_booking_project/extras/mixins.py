from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

class ProtectedView(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProtectedView, self).dispatch(*args, **kwargs)