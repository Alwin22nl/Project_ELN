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
    },

    "skinformation": {
        "label": "Huidvorming",
        "has_afterstorage": True,
        "fields": {
            "skinformation_time": "Huidvorming",
            "tack_free_time": "Tack Free"
        }
    },

    "curability": {
        "label": "uitharding",
        "has_afterstorage": True,
        "fields": {
            "day_1": "1 Dag",
            "day_7": "7 Dagen" 
        }
    },

    "initial_tack": {
        "label": "Initial Tack",
        "has_afterstorage": False,
        "fields": {
            "initial_tack": "Initail Tack"
        }
    },

    "adhesion": {
        "label": "Hechting",
        "has_afterstorage": False,
        "fields": {
            "rubber": "Rubber",
            "copper": "Koper",
            "wood": "Hout",
            "aluminium": "Aluminium",
            "aluminium_anod": "Aluminium Anod.",
            "lead": "Lood",
            "rvs": "RVS",
            "concrete": "Beton",
            "glass": "Glas",
            "pvc": "PVC",
            "pmma": "PMMA",
            "pc": "Poly Carbonaat"
        }
    },

    "epdm_adhesion": {
        "label": "EPDM Hechting",
        "has_afterstorage": False,
        "fields": {
            "europees": "EU-EPDM",
            "trc": "TRC-EPDM",
            "carlisle": "Carlisle-EPDM",
            "rubber": "Rubber",
            "copper": "Koper",
            "wood": "Hout",
            "aluminium": "Aluminium",
            "aluminium_anod": "Aluminium Anod.",
            "lead": "Lood",
            "rvs": "RVS",
            "concrete": "Beton",
            "glass": "Glas",
            "pvc": "PVC",
            "pmma": "PMMA",
            "pc": "Poly Carbonaat"
        }
    },

    "tensile": {
        "label": "Trecksterkte",
        "has_afterstorage": False,
        "result_type": "specimen_avarage",
        "expected_specimens": 4,
        "exclude_on_remark": True,
        "fields": {
            "t_50": "T50 Gemiddelde",
            "t_100": "T100 Gemiddelde",
            "t_max": "T MAX Gemiddelde",
            "e_max": "E MAX Gemiddelde"
        }
    }
}