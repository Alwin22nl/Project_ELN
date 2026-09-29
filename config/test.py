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
        }
    }
}