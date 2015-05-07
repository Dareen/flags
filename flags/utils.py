from flags.conf import settings


def get_key(application, key):
    return ":".join(
        map(str, filter(None, [settings.PREFIX, settings.VERSION,
                               application, key]))
    )

def get_list_key(application):
    return settings.FLAGS_LIST_KEY % application
