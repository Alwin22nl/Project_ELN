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
        "endpoint": "curability", 
    },
    {
        "name": "Treksterkte",
        "endpoint": "tensile",
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