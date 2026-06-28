import django.dispatch

original_signal_init = django.dispatch.Signal.__init__
def new_signal_init(self, *args, **kwargs):
    kwargs.pop('providing_args', None)
    return original_signal_init(self, *args, **kwargs)
django.dispatch.Signal.__init__ = new_signal_init
