from django.dispatch import Signal, receiver

init_api_model = Signal(providing_args=["name", ])


@receiver(init_api_model)
def on_init_api_model(sender, **kwargs):
    print "inited"