# Hospital resource data for India (States/UTs)
# This file provides hospital counts and detailed resource breakdowns for use in planning agents.

HOSPITAL_COUNTS = [
    {"States/UTs": "Lakshadweep", "Number of hospitals in public sector": 9, "Number of hospitals in private sector": 4, "Total number of hospitals (public+private)": 13},
    {"States/UTs": "Chandigarh", "Number of hospitals in public sector": 9, "Number of hospitals in private sector": 4, "Total number of hospitals (public+private)": 13},
    {"States/UTs": "Dadra & N Haveli", "Number of hospitals in public sector": 12, "Number of hospitals in private sector": 6, "Total number of hospitals (public+private)": 18},
    {"States/UTs": "Puducherry", "Number of hospitals in public sector": 14, "Number of hospitals in private sector": 6, "Total number of hospitals (public+private)": 20},
    {"States/UTs": "Daman & Diu", "Number of hospitals in public sector": 5, "Number of hospitals in private sector": 21, "Total number of hospitals (public+private)": 26},
    {"States/UTs": "Andaman Nicobar Islands", "Number of hospitals in public sector": 30, "Number of hospitals in private sector": 6, "Total number of hospitals (public+private)": 36},
    {"States/UTs": "Manipur", "Number of hospitals in public sector": 30, "Number of hospitals in private sector": 8, "Total number of hospitals (public+private)": 38},
    {"States/UTs": "Sikkim", "Number of hospitals in public sector": 33, "Number of hospitals in private sector": 8, "Total number of hospitals (public+private)": 41},
    {"States/UTs": "Nagaland", "Number of hospitals in public sector": 36, "Number of hospitals in private sector": 13, "Total number of hospitals (public+private)": 49},
    {"States/UTs": "Goa", "Number of hospitals in public sector": 43, "Number of hospitals in private sector": 22, "Total number of hospitals (public+private)": 65},
    {"States/UTs": "Mizoram", "Number of hospitals in public sector": 90, "Number of hospitals in private sector": 23, "Total number of hospitals (public+private)": 113},
    {"States/UTs": "Jammu & Kashmir", "Number of hospitals in public sector": 143, "Number of hospitals in private sector": 14, "Total number of hospitals (public+private)": 157},
    {"States/UTs": "Tripura", "Number of hospitals in public sector": 156, "Number of hospitals in private sector": 8, "Total number of hospitals (public+private)": 164},
    {"States/UTs": "Delhi", "Number of hospitals in public sector": 109, "Number of hospitals in private sector": 67, "Total number of hospitals (public+private)": 176},
    {"States/UTs": "Meghalaya", "Number of hospitals in public sector": 157, "Number of hospitals in private sector": 28, "Total number of hospitals (public+private)": 185},
    {"States/UTs": "Arunachal Pradesh", "Number of hospitals in public sector": 218, "Number of hospitals in private sector": 20, "Total number of hospitals (public+private)": 238},
    {"States/UTs": "Chhattisgarh", "Number of hospitals in public sector": 214, "Number of hospitals in private sector": 1822, "Total number of hospitals (public+private)": 396},
    {"States/UTs": "Andhra Pradesh", "Number of hospitals in public sector": 258, "Number of hospitals in private sector": 670, "Total number of hospitals (public+private)": 928},
    {"States/UTs": "Madhya Pradesh", "Number of hospitals in public sector": 465, "Number of hospitals in private sector": 506, "Total number of hospitals (public+private)": 971},
    {"States/UTs": "Himachal Pradesh 8", "Number of hospitals in public sector": 801, "Number of hospitals in private sector": 235, "Total number of hospitals (public+private)": "1,036"},
    {"States/UTs": "Uttarakhand", "Number of hospitals in public sector": 460, "Number of hospitals in private sector": 829, "Total number of hospitals (public+private)": "1,289"},
    {"States/UTs": "Jharkhand", "Number of hospitals in public sector": 555, "Number of hospitals in private sector": 809, "Total number of hospitals (public+private)": "1,364"},
    {"States/UTs": "Gujarat", "Number of hospitals in public sector": 438, "Number of hospitals in private sector": 970, "Total number of hospitals (public+private)": "1,408"},
    {"States/UTs": "Assam", "Number of hospitals in public sector": "1,226", "Number of hospitals in private sector": 503, "Total number of hospitals (public+private)": "1,729"},
    {"States/UTs": "Haryana", "Number of hospitals in public sector": 668, "Number of hospitals in private sector": "1,480", "Total number of hospitals (public+private)": "2,148"},
    {"States/UTs": "West Bengal", "Number of hospitals in public sector": "1,566", "Number of hospitals in private sector": 697, "Total number of hospitals (public+private)": "2,263"},
    {"States/UTs": "Punjab", "Number of hospitals in public sector": 682, "Number of hospitals in private sector": "1,638", "Total number of hospitals (public+private)": "2,320"},
    {"States/UTs": "Tamil Nadu", "Number of hospitals in public sector": "1,217", "Number of hospitals in private sector": "1,222", "Total number of hospitals (public+private)": "2,439"},
    {"States/UTs": "Odisha", "Number of hospitals in public sector": "1,806", "Number of hospitals in private sector": 695, "Total number of hospitals (public+private)": "2,501"},
    {"States/UTs": "Bihar", "Number of hospitals in public sector": "1,147", "Number of hospitals in private sector": "1,887", "Total number of hospitals (public+private)": "3,034"},
    {"States/UTs": "Maharashtra", "Number of hospitals in public sector": 711, "Number of hospitals in private sector": "2,492", "Total number of hospitals (public+private)": "3,203"},
    {"States/UTs": "Kerala", "Number of hospitals in public sector": "1,280", "Number of hospitals in private sector": "2,062", "Total number of hospitals (public+private)": "3,342"},
    {"States/UTs": "Telangana", "Number of hospitals in public sector": 863, "Number of hospitals in private sector": "3,247", "Total number of hospitals (public+private)": "4,110"},
    {"States/UTs": "Rajasthan", "Number of hospitals in public sector": "2,850", "Number of hospitals in private sector": "2,794", "Total number of hospitals (public+private)": "5,644"},
    {"States/UTs": "Karnataka", "Number of hospitals in public sector": "2,842", "Number of hospitals in private sector": "7,842", "Total number of hospitals (public+private)": "10,684"},
    {"States/UTs": "Uttar Pradesh", "Number of hospitals in public sector": "4,635", "Number of hospitals in private sector": "12,468", "Total number of hospitals (public+private)": "17,103"},
    {"States/UTs": "Ladakh", "Number of hospitals in public sector": "NA", "Number of hospitals in private sector": "NA", "Total number of hospitals (public+private)": "NA"}
]

RESOURCE_BREAKDOWN = [
    {"Classification": "Hospitals", "DME": 50, "DMRHS": 330, "DPH": "NA", "ESI": 7, "Total": 387},
    {"Classification": "Dispensaries", "DME": 13, "DMRHS": 11, "DPH": "NA", "ESI": 214, "Total": 238},
    {"Classification": "Primary Health Centres", "DME": 0, "DMRHS": 0, "DPH": 1806, "ESI": 0, "Total": 1806},
    {"Classification": "Health Sub-Centres", "DME": 0, "DMRHS": 0, "DPH": 8706, "ESI": 0, "Total": 8706},
    {"Classification": "Mobile Medical Units", "DME": 0, "DMRHS": 0, "DPH": 416, "ESI": 0, "Total": 416},
    {"Classification": "Bed Strength", "DME": 36881, "DMRHS": 32235, "DPH": 23496, "ESI": 1125, "Total": 93737},
    {"Classification": "Number of Doctors", "DME": 7430, "DMRHS": 4073, "DPH": 6350, "ESI": 695, "Total": 18548},
    {"Classification": "Number of Nurses", "DME": 9335, "DMRHS": 7574, "DPH": 19177, "ESI": 523, "Total": 36609}
]

def get_hospital_count(state: str):
    """Return hospital count info for a given state/UT."""
    for entry in HOSPITAL_COUNTS:
        if entry["States/UTs"].lower().replace(" ","") == state.lower().replace(" ",""):
            return entry
    return None

def get_resource_breakdown(classification: str):
    """Return resource breakdown for a given classification (e.g., 'Hospitals', 'Bed Strength')."""
    for entry in RESOURCE_BREAKDOWN:
        if entry["Classification"].lower() == classification.lower():
            return entry
    return None
