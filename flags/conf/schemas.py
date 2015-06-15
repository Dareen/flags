from schema import Schema, Optional

# TODO: Schemas should be dynamic based on the application specific segmentation
flags_schema = Schema({
    "enabled": bool,
    Optional("segmentation"): {
        Optional(basestring): {
            "enabled": bool,
            Optional("options"): {
                Optional(basestring): bool
            }
        }
    }
})
