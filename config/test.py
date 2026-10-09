TEST_PAGES = [
    {
        "name": "Rheologie",
        "endpoint": "rheology.rheology",
    },
    {
        "name": "Huidvorming",
        "endpoint": "skinformation.skinformation",
    },
    {
        "name": "Initial Tack",
        "endpoint": "initial_tack.initial_tack",
    },
    {
        "name": "Dichtheid",
        "endpoint": "density.density",
    },
    {
        "name": "Shore A",
        "endpoint": "shore_a.shore_a",
    },
    {
        "name": "Hechting",
        "endpoint": "adhesion.adhesion",
    },
    {
        "name": "EPDM Hechting",
        "endpoint": "epdm_adhesion.epdm_adhesion", 
    },

    {
        "name": "Uitharding",
        "endpoint": "curability.curability", 
    },
    {
        "name": "Treksterkte",
        "endpoint": "tensile.tensile",
    }       
]

OVERVIEW_TESTS = {
    1: {
        "header": "Yield Stress",
        "field": "yield_stress"
    },
    2: {
        "header": "Uitharding 1d",
        "field": "day_1"
    },
    3: {
        "header": "Shore A",
        "field": "shore_a_avg"
    },
    4: {
        "header": "Dichtheid",
        "field": "density_product"
    },
    5: {
        "header": "T-Max",
        "field": "t_max"
    },
    6: {
        "header": "Hechting",
        "field": "adhesion"
    },
    7: {
        "header": "EPDM Hechting",
        "field": "epdm_adhesion"
    },
    8: {
        "header": "Initial Tack",
        "field": "initial_tack"
    },
    9: {
        "header": "Huidvorming",
        "field": "skinformation_time"
    }
}

TEST_CONFIG = {
    "samples": {
        "label": "Sample",
        "table": "samples",
        "id_column": "sample_id",
        "has_afterstorage": False,

        "fields": {
            "batch_nr": "Batch Nummer",
            "prod_date": "Productie datum",
            "after_storage_required": "Afterstorage"
        } 
    },
    "rheology": {
        "label": "Rheology",
        "table": "rheology",
        "id_column": "rheology_id",
        "has_afterstorage": True,

        "fields": {
            "yield_stress": "Yield stress",
            "vis_at_1": "Viscositeit @ 1",
            "vis_at_5": "Viscositeit @ 5",
            "vis_at_10": "Viscositeit @ 10",
            "humidity": "Luchtvochtigheid"
        }
    },
    "skinformation" : {
        "label": "Huidvorming",
        "table": "skinformation",
        "id_column": "skinformation_id",
        "has_afterstorage": True,
        "fields": {
            "skinformation_time": "Huidvorming tijd",
            "temp_skinformation_time": "Temp Huidvorming",
            "rh_skinformation_time": "%RH Huidvorming",
            "tack_free_time": "Tack Free Tijd",
            "temp_tack_free_time": "Temp Tack Free",
            "rh_tack_free_time": "%RH Tack Free"
        }
    },
    "curability" : {
        "label": "Uitharding",
        "table": "curability",
        "id_column": "cureability_id",
        "has_afterstorage": True,
        "fields": {
            "day_1": "1 Dag",
            "temp_day1": "Temp 1 dag",
            "rh_day1": "%RH 1 dag",
            "day_7": "7 Dagen",
            "temp_day7": "Temp 7 dagen",
            "rh_day7": "%RH 7 dagen"
        }
    },
    "shore_a": {
        "label": "Shore A",
        "table": "shore_a",
        "id_column": "shore_a_id",
        "has_afterstorage": False,
        "fields": {
            "shore_a_1": "Shore A 1",
            "shore_a_2": "Shore A 2",
            "shore_a_3": "Shore A 3",
            "temperature": "Temperatuur",
            "humidity": "Luchtvochtigheid"
        },
        "recalculate": {
            "field": "shore_a_avg",
            "source_fields": [
                "shore_a_1",
                "shore_a_2",
                "shore_a_3"
            ]
        }
    },
    "density": {
        "label": "Dichtheid",
        "table": "density",
        "id_column": "density_id",
        "has_afterstorage": False,
        "fields": {
            "vessel_empty": "Gewicht Leeg",
            "vessel_full": "Gewicht Vol",
            "vessel_volume": "Volume"
        },
        "recalculate": {
                    "field": "density_product",
                    "source_fields": [
                        "vessel_empty",
                        "vessel_full",
                        "vessel_volume"
                    ]
                }
    },
    "initial_tack": {
        "label": "Initial Tack",
        "table": "initial_tack",
        "id_column": "initial_tack_id",
        "has_afterstorage": False,
        "fields": {
            "area": "Oppervlak",
            "area_weight": "Gewicht Opp.",
            "added_weight": "Toegevoegt Gewicht",
            "humidity": "Luchtvochtigheid"
        },
        "recalculate": {
                    "field": "initial_tack",
                    "source_fields": [
                        "area",
                        "area_weight",
                        "added_weight"
                    ]
                }
    },
    "adhesion": {
        "label": "Hechting",
        "table": "adhesion",
        "id_column": "adhesion_id",
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
            "pc": "PC"
        }
    },
    "epdm_adhesion": {
        "label": "EPDM Hechting",
        "table": "epdm_adhesion",
        "id_column": "epdm_adhesion_id",
        "has_afterstorage": False,

        "fields": {
            "europees": "EPDM-EU",
            "trc": "EPDM-TRC",
            "carlisle": "EPDM-Carlisle",
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
            "pc": "PC"
        }
    },
    "tensile": {
        "label": "Tensile",
        "special_type": "specimens",

        "table": "tensile_specimen",
        "id_column": "specimen_id",
        "specimen_column": "specimen_no",
        "has_afterstorage": False,

        "fields": {
            "width_1": "Breedte 1",
            "width_2": "Breedte 2",
            "width_3": "Breedte 3",

            "thickness_1": "Dikte 1",
            "thickness_2": "Dikte 2",
            "thickness_3": "Dikte 3",

            "t_50": "T 50",
            "t_100": "T 100",
            "t_max": "T MAX",
            "e_max": "E MAX"
        },

        "recalculate": {
            "width": {
                "trigger_fields": [
                    "width_1",
                    "width_2",
                    "width_3"
                ],
                "result_field": "width_avg",
                "round": 2
            },

            "thickness": {
                "trigger_fields": [
                    "thickness_1",
                    "thickness_2",
                    "thickness_3"
                ],
                "result_field": "thickness_avg",
                "round": 2
            }
        }
    }
}

TEST_TABLES = {
    "rheology": "rheology",
    "skinformation": "skinformation",
    "curability": "curability",
    "density": "density",
    "initial_tack": "initial_tack",
    "shore_a": "shore_a",
    "tensile_strength": "tensile_strength",
    "adhesion": "adhesion",
    "epdm_adhesion": "epdm_adhesion"
}

NOTIFICATION_CONFIG = {

    "change_request": {
        "title": "Wijzigingsaanvragen",
        "message": (
            "1 of meerdere wijzigingsaanvragen "
            "staan klaar voor beoordeling."
        ),
        "link": "/change_request/approvals"
    },

    "product_limit": {
        "title": "Product-limieten",
        "message": (
            "1 of meerdere batches hebben een "
            "resultaat buiten de limieten."
        ),
        "link": "/quality/limit-triggers"
    }
}
