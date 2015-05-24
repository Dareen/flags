from schema import Schema, Optional

flags_schema = Schema({
    "enabled": bool,
    "for_all": bool,
    Optional("segmentation"): {
        Optional(basestring): {
            "enabled": bool,
            "for_all": bool,
            Optional("options"): {
                Optional(basestring): bool
            }
        }
    }
})
