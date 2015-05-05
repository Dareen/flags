from flags.conf import settings

def get_key(key):
    return ":".join(
        map(str, filter(None, [settings.PREFIX, settings.VERSION, key]))
    )