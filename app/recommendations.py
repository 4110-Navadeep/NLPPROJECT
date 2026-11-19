"""
Maintenance Decision Support Module for FMC-MWO2KG Equipment Failure Categories.
Maps predicted failure categories to actionable technician inspection protocols,
targeted subsystems, and suggested priority levels.
"""

from typing import Dict, Any, List

# Comprehensive mapping for all 22 FMC-MWO2KG failure categories
MAINTENANCE_RECOMMENDATIONS: Dict[str, Dict[str, Any]] = {
    "Minor in-service problems": {
        "code": "MISP",
        "category": "Minor in-service problems",
        "suggested_priority": "Routine / Medium",
        "status_color": "warning",
        "targeted_subsystem": "General Equipment Fittings & Fasteners",
        "suggestions": [
            "Inspect physical fasteners, brackets, and mounting bolts for looseness.",
            "Verify equipment orientation, alignment, and secure all loose guards.",
            "Inspect sightglasses, indicators, and replace consumable seals if worn.",
            "Schedule descaling or minor lubrication during the next operational window.",
        ],
    },
    "Breakdown": {
        "code": "BRKD",
        "category": "Breakdown",
        "suggested_priority": "Critical / Immediate",
        "status_color": "danger",
        "targeted_subsystem": "Primary Drive & Core Mechanical Assembly",
        "suggestions": [
            "Perform immediate lockout/tagout (LOTO) and halt machinery operation.",
            "Inspect spindle, shaft, and drive coupling for complete mechanical seizure.",
            "Inspect internal gear teeth, bearings, and drive belts for catastrophic breakage.",
            "Conduct full teardown diagnostics before attempting to re-energize.",
        ],
    },
    "Structural deficiency": {
        "code": "STRD",
        "category": "Structural deficiency",
        "suggested_priority": "High Priority",
        "status_color": "danger",
        "targeted_subsystem": "Structural Frame, Mountings & Housing",
        "suggestions": [
            "Inspect machinery frame, baseplates, and load-bearing brackets for micro-cracks.",
            "Check for severe chemical corrosion, rust pitting, or material degradation.",
            "Examine protective shrouds, covers, and structural welds for physical fatigue.",
            "Evaluate structural integrity and repair or reinforce compromised members.",
        ],
    },
    "Electrical": {
        "code": "ELEC",
        "category": "Electrical",
        "suggested_priority": "Critical / Immediate",
        "status_color": "danger",
        "targeted_subsystem": "Electrical Power & Control Distribution",
        "suggestions": [
            "Inspect electrical connections, motor terminals, and power cables for short circuits.",
            "Measure static earth resistance and verify grounding continuity.",
            "Check circuit breakers, thermal overload relays, and inverter trip history.",
            "Inspect junction boxes and terminal blocks for scorching or insulation breakdown.",
        ],
    },
    "Plugged / choked": {
        "code": "PLUG",
        "category": "Plugged / choked",
        "suggested_priority": "High Priority",
        "status_color": "warning",
        "targeted_subsystem": "Fluid Flow, Piping & Filtration System",
        "suggestions": [
            "Inspect intake and discharge lines for solid slurry or sediment accumulation.",
            "Clean or replace clogged line strainers, suction filters, and inline orifices.",
            "Verify valve positioning and ensure no obstructions restrict the primary flow path.",
            "Conduct chemical descaling or mechanical flushing following standard site procedures.",
        ],
    },
    "Leaking": {
        "code": "LEAK",
        "category": "Leaking",
        "suggested_priority": "High Priority",
        "status_color": "warning",
        "targeted_subsystem": "Fluid Seals, Gaskets & Pipe Couplings",
        "suggestions": [
            "Inspect mechanical shaft seals, packing glands, and O-rings for wear or blowout.",
            "Check pipe flanges, fittings, and bleed valves for pressurized fluid spray or seeping.",
            "Verify torque on flange bolts according to manufacturer specifications.",
            "Contain fluid spillage immediately to prevent environmental contamination and slip hazards.",
        ],
    },
    "Failure to start on demand": {
        "code": "FTSD",
        "category": "Failure to start on demand",
        "suggested_priority": "High Priority",
        "status_color": "danger",
        "targeted_subsystem": "Starter Circuit & Control Interlocks",
        "suggestions": [
            "Verify control circuit power supply, starter coils, and emergency stop circuits.",
            "Inspect safety interlocks, permissives, and limit switches preventing start sequence.",
            "Check motor starter contacts, relays, and verify incoming three-phase supply.",
            "Inspect drive shaft by hand (under LOTO) to rule out mechanical jamming.",
        ],
    },
    "Abnormal instrument reading": {
        "code": "ABNR",
        "category": "Abnormal instrument reading",
        "suggested_priority": "Moderate Priority",
        "status_color": "info",
        "targeted_subsystem": "Instrumentation & Telemetry Sensors",
        "suggestions": [
            "Inspect sensor wiring harnesses for loose connectors or sporadic signal drops.",
            "Check sensor calibration against verified reference gauges (temperature/pressure).",
            "Examine sensor probe tips for fouling, scale buildup, or mechanical displacement.",
            "Verify transmitter 4-20mA or digital bus communications with the PLC/SCADA.",
        ],
    },
    "Fail to function": {
        "code": "FTFN",
        "category": "Fail to function",
        "suggested_priority": "High Priority",
        "status_color": "danger",
        "targeted_subsystem": "Actuation & Functional Mechanisms",
        "suggestions": [
            "Inspect pneumatic, hydraulic, or motorized actuators for mechanical stiffness.",
            "Check linkage arms, pivot pins, and guide rails for binding or misalignment.",
            "Verify supply air or hydraulic pressure reaching the operating actuator.",
            "Inspect internal valves or dampers to ensure components move through their full stroke.",
        ],
    },
    "Low output": {
        "code": "LOUT",
        "category": "Low output",
        "suggested_priority": "Moderate Priority",
        "status_color": "warning",
        "targeted_subsystem": "Pump Impeller / Drive Transmission",
        "suggestions": [
            "Check rotational speed (RPM) and verify drive belt tension or motor coupling.",
            "Inspect pump impeller, vanes, or blades for cavitation erosion or excessive clearance.",
            "Examine intake suction head and check for partial cavitation or air ingestion.",
            "Measure discharge pressure and compare against operating pump curve.",
        ],
    },
    "Vibration": {
        "code": "VIBR",
        "category": "Vibration",
        "suggested_priority": "High Priority",
        "status_color": "danger",
        "targeted_subsystem": "Bearings, Shaft Alignment & Rotor Balance",
        "suggestions": [
            "Perform dynamic vibration spectrum analysis (radial, axial, and horizontal).",
            "Inspect bearing assemblies for spalling, cage damage, or insufficient lubrication.",
            "Check shaft alignment between motor and driven equipment using laser alignment tools.",
            "Inspect rotating assembly for dynamic unbalance, blade buildup, or loose mounting bolts.",
        ],
    },
    "Overheating": {
        "code": "OVHT",
        "category": "Overheating",
        "suggested_priority": "Critical / Immediate",
        "status_color": "danger",
        "targeted_subsystem": "Cooling Systems, Lubrication & Heat Dissipation",
        "suggestions": [
            "Inspect cooling fan, airflow cowl, and heat exchanger fins for blockage or debris.",
            "Check bearing and gearbox lubricant levels, viscosity, and thermal degradation.",
            "Verify motor electrical current draw against full-load amp (FLA) rating to detect overload.",
            "Measure surface temperatures across bearings, motor casing, and drive couplings.",
        ],
    },
    "Noise": {
        "code": "NOIS",
        "category": "Noise",
        "suggested_priority": "Moderate Priority",
        "status_color": "info",
        "targeted_subsystem": "Bearings, Gears & Acoustic Enclosure",
        "suggestions": [
            "Use acoustic stethoscope or ultrasound detector to isolate noise source.",
            "Inspect drive belts for slipping, squealing, or improper tension.",
            "Examine gear mesh clearances and inspect teeth for pitting or backlash.",
            "Check internal bearing clearances and inspect for dry or contaminated grease.",
        ],
    },
    "Contamination": {
        "code": "CONT",
        "category": "Contamination",
        "suggested_priority": "Moderate Priority",
        "status_color": "warning",
        "targeted_subsystem": "Lubricant Reservoir & Environmental Enclosures",
        "suggestions": [
            "Sample oil / lubricant to check for moisture ingress, grit, or metal particulate wear.",
            "Inspect oil seals, breathers, and enclosure gaskets for water or dirt penetration.",
            "Flush and replace contaminated lubricating fluid in accordance with OEM instructions.",
            "Clean surrounding equipment bay to prevent external debris accumulation.",
        ],
    },
    "Failure to stop on demand": {
        "code": "FTSOP",
        "category": "Failure to stop on demand",
        "suggested_priority": "Critical / Safety Risk",
        "status_color": "danger",
        "targeted_subsystem": "Safety Braking & Stop Interlock Circuit",
        "suggestions": [
            "Perform emergency stop testing under controlled supervisor conditions.",
            "Inspect mechanical holding brakes, friction pads, and caliper release mechanisms.",
            "Check stop contactors, E-stop pushbuttons, and safety relay circuits for welded contacts.",
            "Inspect control logic and PLC shutdown commands for stuck bit overrides.",
        ],
    },
    "Erratic output": {
        "code": "ERRO",
        "category": "Erratic output",
        "suggested_priority": "Moderate Priority",
        "status_color": "warning",
        "targeted_subsystem": "Speed Control, Governor & Inverter Drive",
        "suggestions": [
            "Inspect variable frequency drive (VFD) output stability, parameter tuning, and filtering.",
            "Check mechanical governor springs, linkages, and throttle control valves.",
            "Inspect process feed stability to rule out surging or cyclic load variations.",
            "Verify sensor feedback loop stability in the proportional-integral (PI) controller.",
        ],
    },
    "Spurious stop": {
        "code": "SPST",
        "category": "Spurious stop",
        "suggested_priority": "High Priority",
        "status_color": "warning",
        "targeted_subsystem": "Safety Interlock Sensors & Trip Modules",
        "suggestions": [
            "Review alarm and event logs to identify which sensor or interlock initiated the trip.",
            "Inspect sensor wiring for loose connections, vibration-induced disconnects, or noise.",
            "Check threshold setpoints for vibration, temperature, or pressure trip switches.",
            "Inspect power supply modules for momentary voltage dips or transients.",
        ],
    },
    "High output": {
        "code": "HOUT",
        "category": "High output",
        "suggested_priority": "Moderate Priority",
        "status_color": "warning",
        "targeted_subsystem": "Pressure Relief & Flow Regulation",
        "suggestions": [
            "Inspect pressure regulating valves, relief valves, and bypass dampening circuits.",
            "Check motor VFD speed settings to ensure equipment is not operating above rated frequency.",
            "Inspect output discharge piping and backpressure regulators.",
            "Recalibrate flow sensors and controller setpoints.",
        ],
    },
    "Fail to close": {
        "code": "FTCL",
        "category": "Fail to close",
        "suggested_priority": "High Priority",
        "status_color": "warning",
        "targeted_subsystem": "Valves, Dampers & Closing Mechanisms",
        "suggestions": [
            "Inspect valve seat and seal surface for foreign object entrapment or scale.",
            "Check return springs, actuator air pressure, and limit switches.",
            "Lubricate valve stem, guide bushings, and actuator linkages.",
            "Exercise valve manually to detect binding or scoring across the seal face.",
        ],
    },
    "Failure to rotate": {
        "code": "FTROT",
        "category": "Failure to rotate",
        "suggested_priority": "Critical / Immediate",
        "status_color": "danger",
        "targeted_subsystem": "Drive Shaft, Bearings & Spindle",
        "suggestions": [
            "Isolate machinery power and check if shaft turns freely by hand.",
            "Inspect bearings for catastrophic seizure or loss of rotational clearance.",
            "Check gearbox for gear tooth jamming or shaft breakage.",
            "Inspect motor rotor and stator for physical contact or clearance collapse.",
        ],
    },
    "Fail to open": {
        "code": "FTOP",
        "category": "Fail to open",
        "suggested_priority": "High Priority",
        "status_color": "warning",
        "targeted_subsystem": "Valves, Dampers & Opening Actuators",
        "suggestions": [
            "Inspect actuator supply pressure, solenoid pilot valves, and electrical signals.",
            "Check valve stem packing for over-tightening or corrosion seizure.",
            "Inspect internal disk, wedge, or butterfly plate for sticking against seat.",
            "Verify positioner feedback signal and stroke calibration.",
        ],
    },
    "Other": {
        "code": "OTHR",
        "category": "Other",
        "suggested_priority": "Routine / Review",
        "status_color": "neutral",
        "targeted_subsystem": "Auxiliary Machinery Components",
        "suggestions": [
            "Conduct a comprehensive general physical inspection of all equipment subsystems.",
            "Review historical maintenance logs for previous intermittent complaints.",
            "Verify all sensor calibrations and mechanical connections.",
            "Refer to the equipment maintenance manual for specialized inspection procedures.",
        ],
    },
}

DEFAULT_GUIDANCE = {
    "code": "GEN",
    "category": "General Equipment Anomaly",
    "suggested_priority": "Suggested Inspection Priority: Standard Review",
    "status_color": "neutral",
    "targeted_subsystem": "General Equipment Subassembly",
    "suggestions": [
        "Further inspection is recommended. Refer to the equipment maintenance manual.",
        "Perform a thorough visual and audible inspection across all accessible components.",
        "Verify baseline operational parameters against standard engineering tolerances.",
    ],
}

MAINTENANCE_DISCLAIMER = (
    "Disclaimer: These maintenance recommendations are general suggested priorities and inspection guidance "
    "to support technician decision-making. They do not constitute a confirmed risk assessment, guaranteed automated "
    "diagnosis, or certified repair instruction. Always follow approved site safety procedures and OEM manuals."
)


def get_recommendations_for_category(category_name: str) -> Dict[str, Any]:
    """
    Retrieve inspection guidance for a given predicted FMC-MWO2KG failure category.
    """
    clean_cat = category_name.strip()
    data = MAINTENANCE_RECOMMENDATIONS.get(clean_cat)
    if not data:
        data = dict(DEFAULT_GUIDANCE)
        data["category"] = clean_cat

    return {
        "code": data["code"],
        "category": data["category"],
        "suggested_priority": data["suggested_priority"],
        "status_color": data["status_color"],
        "targeted_subsystem": data["targeted_subsystem"],
        "suggestions": data["suggestions"],
        "disclaimer": MAINTENANCE_DISCLAIMER,
    }
