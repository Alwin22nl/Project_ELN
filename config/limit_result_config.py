LIMIT_RESULT_CONFIG = {

    "density": {
        "label": "Dichtheid",
        "has_afterstorage": False,
        "fields": {
            "density_product": "Dichtheid"
        }
    },

    "shore_a": {
        "label": "Shore A",
        "has_afterstorage": False,
        "fields": {
            "shore_a_avg": "Shore A Gemiddelde"
        }
    },

    "rheology": {
        "label": "Rheology",
        "has_afterstorage": True,
        "fields": {
            "yield_stress": "Yield Stress",
            "vis_at_1": "Viscositeit @ 1",
            "vis_at_5": "Viscositeit @ 5",
            "vis_at_10": "Viscositeit @ 10"
        }
    }
}