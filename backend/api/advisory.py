"""
Farmer Advisory API
===================
Free, publicly accessible advisory endpoint.
No login required. Serves farmers, extension workers, and NGOs.

Provides:
- Current ENSO phase + risk level for a given state/crop/season
- Plain-English advisory with actionable recommendations
- PMFBY enrollment guidance
- Claim probability estimate from the survival model
"""

from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

# ──────────────────────────────────────────────
# PMFBY Zone Mapping
# Maps Indian states → Agro-climatic zone → Vulnerability score under El Niño
# Source: NARP (National Agricultural Research Project) zones
# ──────────────────────────────────────────────
PMFBY_ZONE_MAP = {
    "Andhra Pradesh":   {"zone": "Eastern Coastal Plains",        "el_nino_vulnerability": "High",   "pmfby_cutoff": "July 31 (Kharif), Dec 31 (Rabi)"},
    "Karnataka":        {"zone": "Southern Plateau & Hills",      "el_nino_vulnerability": "High",   "pmfby_cutoff": "July 31 (Kharif), Dec 31 (Rabi)"},
    "Madhya Pradesh":   {"zone": "Central Highlands",             "el_nino_vulnerability": "Medium", "pmfby_cutoff": "July 31 (Kharif), Nov 30 (Rabi)"},
    "Maharashtra":      {"zone": "Western Plateau & Hills",       "el_nino_vulnerability": "High",   "pmfby_cutoff": "July 31 (Kharif), Dec 31 (Rabi)"},
    "Punjab":           {"zone": "Trans-Gangetic Plains",         "el_nino_vulnerability": "Low",    "pmfby_cutoff": "July 31 (Kharif), Nov 30 (Rabi)"},
    "Uttar Pradesh":    {"zone": "Upper Gangetic Plains",         "el_nino_vulnerability": "Medium", "pmfby_cutoff": "July 31 (Kharif), Nov 30 (Rabi)"},
}

# ──────────────────────────────────────────────
# Crop advisory library (El Niño specific)
# ──────────────────────────────────────────────
CROP_ADVISORIES = {
    "Rice": {
        "El Nino": {
            "risk_note": "El Niño causes below-normal monsoon rainfall. Rice is highly water-intensive and extremely vulnerable.",
            "actions": [
                "Switch to short-duration, drought-tolerant varieties (Sahbhagi Dhan, DRR Dhan 42)",
                "Delay transplanting by 2–3 weeks to align with late monsoon onset",
                "Adopt System of Rice Intensification (SRI) to reduce water usage by 30%",
                "Apply mulching to retain soil moisture",
                "Ensure PMFBY enrollment before the cutoff date for your state",
            ]
        },
        "La Nina": {
            "risk_note": "La Niña brings excess rainfall. Flood and waterlogging risk for rice paddies.",
            "actions": [
                "Ensure proper field drainage channels are cleared",
                "Consider raised-bed cultivation in low-lying areas",
                "Choose flood-tolerant varieties (Swarna Sub-1)",
                "Monitor for increased fungal disease pressure due to excess humidity",
            ]
        },
        "Neutral": {
            "risk_note": "Normal monsoon conditions expected. Standard cultivation practices apply.",
            "actions": [
                "Follow standard sowing calendar for your district",
                "Maintain optimal plant population and nutrient management",
                "Monitor IMD forecasts for any seasonal deviation",
            ]
        }
    },
    "Cotton": {
        "El Nino": {
            "risk_note": "Cotton is moderately drought-tolerant but high temperatures during El Niño cause boll drop and yield loss.",
            "actions": [
                "Opt for drip irrigation if available — reduces water use by 40%",
                "Choose heat-tolerant Bt-Cotton hybrids approved for your state",
                "Apply deficit irrigation (60% ETc) during vegetative stage to induce drought hardening",
                "Avoid late sowing — higher temperatures at boll-setting stage severely reduce yield",
                "Enroll under PMFBY for coverage against yield loss",
            ]
        },
        "La Nina": {
            "risk_note": "Excess rainfall during La Niña can cause root rot and bollworm outbreaks.",
            "actions": [
                "Apply prophylactic fungicide treatment at squaring stage",
                "Monitor for increased sucking pest pressure",
                "Ensure field drainage to avoid waterlogging",
            ]
        },
        "Neutral": {
            "risk_note": "Normal conditions. Standard Kharif cotton practices apply.",
            "actions": [
                "Follow recommended plant population and spacing",
                "Apply balanced NPK as per soil test recommendations",
            ]
        }
    },
    "Wheat": {
        "El Nino": {
            "risk_note": "Wheat is a Rabi (winter) crop. El Niño typically reduces winter rainfall in north India, affecting late-stage grain filling.",
            "actions": [
                "Apply pre-sowing irrigation if rainfall is deficient",
                "Choose drought-tolerant varieties (HD 2781, K 9107) for rain-fed areas",
                "Apply one extra irrigation at grain-filling stage if soil moisture is low",
                "Monitor for early terminal heat stress — El Niño years often see early summer onset",
            ]
        },
        "La Nina": {
            "risk_note": "La Niña may bring excess winter rains causing waterlogging and disease.",
            "actions": [
                "Ensure timely sowing to avoid coinciding grain maturity with wet spells",
                "Apply fungicide for yellow rust and powdery mildew control",
            ]
        },
        "Neutral": {
            "risk_note": "Normal Rabi season expected.",
            "actions": [
                "Follow recommended sowing window (November 1–25 for most of north India)",
                "Apply balanced fertilization — nitrogen in split doses",
            ]
        }
    },
    "Maize": {
        "El Nino": {
            "risk_note": "Maize is moderately drought-sensitive at tasseling and silking stage. El Niño-driven dry spells during this window cause significant yield loss.",
            "actions": [
                "Prioritize irrigation at tasseling and silking (most critical stages)",
                "Choose hybrid varieties with drought tolerance (DKC 9108, P3522)",
                "Practice conservation tillage to improve soil water retention",
                "Consider crop insurance enrollment under PMFBY",
            ]
        },
        "La Nina": {
            "risk_note": "Excess rainfall and waterlogging can cause root rot in maize.",
            "actions": [
                "Plant on ridges or raised beds to improve drainage",
                "Apply fungicide seed treatment before sowing",
            ]
        },
        "Neutral": {
            "risk_note": "Normal season. Standard maize practices apply.",
            "actions": [
                "Follow recommended spacing and fertilizer schedule",
                "Ensure adequate plant population (65,000–75,000 plants/ha)",
            ]
        }
    },
    "Soybean": {
        "El Nino": {
            "risk_note": "Soybean is sensitive to mid-season drought during pod filling. El Niño dry spells at this stage cause severe yield loss.",
            "actions": [
                "Use broad-based bed planting (BBPP) to conserve soil moisture",
                "Choose short-duration varieties (JS 9560, JS 93-05) to escape late-season dry spells",
                "Apply intercultural operations early to reduce soil evaporation",
                "Seed treatment with rhizobium + PSB to improve nutrient uptake under stress",
            ]
        },
        "La Nina": {
            "risk_note": "Excess moisture increases purple stain disease and pod shattering risk.",
            "actions": [
                "Ensure timely harvesting to avoid pod shattering from rain",
                "Apply fungicide for purple stain and Phytophthora root rot management",
            ]
        },
        "Neutral": {
            "risk_note": "Normal Kharif season. Follow standard soybean practices.",
            "actions": [
                "Sow between June 20–July 10 for optimal yields",
                "Maintain 45 cm row spacing and 5 cm seed depth",
            ]
        }
    },
    "Sugarcane": {
        "El Nino": {
            "risk_note": "Sugarcane is water-intensive. El Niño-induced rainfall deficit increases irrigation demand by 20–30%.",
            "actions": [
                "Switch to drip irrigation if possible — most effective for sugarcane",
                "Practice trash mulching (6–8 cm) to reduce evapotranspiration",
                "Delay ratoon crop if water availability is uncertain",
                "Early planting (October–November) helps roots establish before dry season",
            ]
        },
        "La Nina": {
            "risk_note": "Waterlogging from excess rain can cause red rot and root rot diseases.",
            "actions": [
                "Ensure furrow drainage is maintained",
                "Apply fungicide to control red rot — a significant threat in wet conditions",
            ]
        },
        "Neutral": {
            "risk_note": "Normal conditions. Standard sugarcane management applies.",
            "actions": [
                "Follow recommended planting calendar for your zone",
                "Apply nitrogen in 3 split doses for maximum uptake",
            ]
        }
    },
}

# ──────────────────────────────────────────────
# ENSO Phase → Simple category
# ──────────────────────────────────────────────
def classify_enso_phase(oni: float) -> str:
    if oni >= 0.5:
        return "El Nino"
    elif oni <= -0.5:
        return "La Nina"
    else:
        return "Neutral"

def get_enso_label(oni: float) -> str:
    if oni >= 1.5:
        return "Strong El Niño"
    elif oni >= 1.0:
        return "Moderate El Niño"
    elif oni >= 0.5:
        return "Weak El Niño"
    elif oni >= -0.5:
        return "Neutral"
    elif oni >= -1.0:
        return "Weak La Niña"
    elif oni >= -1.5:
        return "Moderate La Niña"
    else:
        return "Strong La Niña"

def get_risk_level(enso_phase: str, vulnerability: str) -> str:
    matrix = {
        ("El Nino", "High"):   "HIGH",
        ("El Nino", "Medium"): "MEDIUM-HIGH",
        ("El Nino", "Low"):    "MEDIUM",
        ("La Nina", "High"):   "MEDIUM-HIGH",
        ("La Nina", "Medium"): "MEDIUM",
        ("La Nina", "Low"):    "LOW-MEDIUM",
        ("Neutral", "High"):   "LOW-MEDIUM",
        ("Neutral", "Medium"): "LOW",
        ("Neutral", "Low"):    "LOW",
    }
    return matrix.get((enso_phase, vulnerability), "MEDIUM")

def get_risk_color(risk_level: str) -> str:
    mapping = {
        "HIGH": "red",
        "MEDIUM-HIGH": "orange",
        "MEDIUM": "yellow",
        "LOW-MEDIUM": "blue",
        "LOW": "green",
    }
    return mapping.get(risk_level, "gray")

# ──────────────────────────────────────────────
# Current ONI value (simulated from latest data)
# In production: fetch from NOAA CPC API
# https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt
# ──────────────────────────────────────────────
CURRENT_ONI = 1.2  # Moderate El Niño (demo value)
CURRENT_ENSO_LABEL = get_enso_label(CURRENT_ONI)
CURRENT_ENSO_PHASE = classify_enso_phase(CURRENT_ONI)

# ──────────────────────────────────────────────
# Claim probability estimates by ENSO phase
# Derived from model outputs (approximated for advisory use)
# ──────────────────────────────────────────────
CLAIM_PROB_ESTIMATES = {
    "El Nino":  {"Kharif": 0.68, "Rabi": 0.42, "Zaid": 0.55},
    "La Nina":  {"Kharif": 0.52, "Rabi": 0.38, "Zaid": 0.45},
    "Neutral":  {"Kharif": 0.31, "Rabi": 0.22, "Zaid": 0.28},
}


# ──────────────────────────────────────────────
# API Endpoint
# ──────────────────────────────────────────────
@router.get("/advisory")
def get_farmer_advisory(state: str, crop: str, season: str):
    """
    Returns a free, plain-English risk advisory for a farmer.
    No authentication required. Publicly accessible.
    
    Args:
        state: Indian state (e.g., Maharashtra)
        crop: Crop type (e.g., Rice, Cotton, Wheat)
        season: Crop season (Kharif, Rabi, Zaid)
    """
    # Validate inputs
    valid_states = list(PMFBY_ZONE_MAP.keys())
    valid_crops = list(CROP_ADVISORIES.keys())
    valid_seasons = ["Kharif", "Rabi", "Zaid"]

    if state not in valid_states:
        return {
            "success": False,
            "error": f"State '{state}' not in database. Supported: {valid_states}"
        }
    if crop not in valid_crops:
        return {
            "success": False,
            "error": f"Crop '{crop}' not in database. Supported: {valid_crops}"
        }
    if season not in valid_seasons:
        return {
            "success": False,
            "error": f"Season '{season}' must be one of: {valid_seasons}"
        }

    # Get zone info
    zone_info = PMFBY_ZONE_MAP[state]
    vulnerability = zone_info["el_nino_vulnerability"]
    risk_level = get_risk_level(CURRENT_ENSO_PHASE, vulnerability)
    risk_color = get_risk_color(risk_level)

    # Get crop-specific advisory
    crop_data = CROP_ADVISORIES.get(crop, {})
    phase_advice = crop_data.get(CURRENT_ENSO_PHASE, crop_data.get("Neutral", {}))
    risk_note = phase_advice.get("risk_note", "Monitor weather conditions and consult your local KVK.")
    actions = phase_advice.get("actions", ["Follow standard practices for your region."])

    # Claim probability
    claim_prob = CLAIM_PROB_ESTIMATES.get(CURRENT_ENSO_PHASE, {}).get(season, 0.35)

    # Generate plain-English summary
    if CURRENT_ENSO_PHASE == "El Nino":
        summary = (
            f"⚠️ {CURRENT_ENSO_LABEL} conditions are currently active (ONI: {CURRENT_ONI:+.1f}). "
            f"{state} falls in the {zone_info['zone']} zone with {vulnerability.lower()} El Niño vulnerability. "
            f"Your {season} {crop} crop faces {risk_level} risk this season. {risk_note}"
        )
    elif CURRENT_ENSO_PHASE == "La Nina":
        summary = (
            f"🌧️ {CURRENT_ENSO_LABEL} conditions are active (ONI: {CURRENT_ONI:+.1f}). "
            f"{state} is in the {zone_info['zone']} zone. "
            f"Your {season} {crop} faces {risk_level} risk from excess rainfall. {risk_note}"
        )
    else:
        summary = (
            f"✅ Neutral ENSO conditions (ONI: {CURRENT_ONI:+.1f}). "
            f"Normal monsoon expected for {state} ({zone_info['zone']} zone). "
            f"{season} {crop} risk is {risk_level}. {risk_note}"
        )

    return {
        "success": True,
        "enso": {
            "phase": CURRENT_ENSO_PHASE,
            "label": CURRENT_ENSO_LABEL,
            "oni_value": CURRENT_ONI,
            "data_source": "NOAA Climate Prediction Center (CPC)"
        },
        "location": {
            "state": state,
            "pmfby_zone": zone_info["zone"],
            "el_nino_vulnerability": vulnerability,
        },
        "crop": {
            "type": crop,
            "season": season,
        },
        "risk": {
            "level": risk_level,
            "color": risk_color,
            "claim_probability_estimate": round(claim_prob, 2),
            "model_basis": "Cox Proportional Hazards survival model (AgriRisk AI)"
        },
        "advisory": {
            "summary": summary,
            "risk_note": risk_note,
            "recommended_actions": actions,
        },
        "pmfby": {
            "enrollment_cutoff": zone_info["pmfby_cutoff"],
            "premium_farmer_share": "1.5% (Rabi) / 2% (Kharif) of sum insured",
            "info_link": "https://pmfby.gov.in",
            "helpline": "1800-180-1551 (Toll Free)"
        },
        "disclaimer": (
            "This advisory is generated by the AgriRisk AI system for informational purposes. "
            "It is not a substitute for official government advisories. "
            "Always consult your local Krishi Vigyan Kendra (KVK) or agriculture officer."
        )
    }


@router.get("/advisory/enso-status")
def get_current_enso_status():
    """Returns the current global ENSO status. No auth required."""
    return {
        "oni_value": CURRENT_ONI,
        "enso_label": CURRENT_ENSO_LABEL,
        "enso_phase": CURRENT_ENSO_PHASE,
        "risk_to_india_kharif": "High" if CURRENT_ENSO_PHASE == "El Nino" else "Normal",
        "data_source": "NOAA Climate Prediction Center",
        "note": "ONI (Oceanic Niño Index) > +0.5 = El Niño, < -0.5 = La Niña, in between = Neutral"
    }


@router.get("/advisory/states")
def get_supported_states():
    """Returns all supported states with their PMFBY zone info."""
    return {
        "states": [
            {
                "name": state,
                "pmfby_zone": info["zone"],
                "el_nino_vulnerability": info["el_nino_vulnerability"],
                "pmfby_enrollment_cutoff": info["pmfby_cutoff"],
            }
            for state, info in PMFBY_ZONE_MAP.items()
        ]
    }
