"""
Custom Tool for Class Attendance Calculation.
Calculates percentage, status against a threshold, required consecutive classes to reach target,
and safe bunkable classes allowance.
"""

import math
from typing import Dict, Any, Union
from langchain_core.tools import tool


def compute_attendance_stats(attended: int, total: int, target_pct: float = 75.0) -> Dict[str, Any]:
    """
    Core mathematical logic for class attendance.
    """
    if total <= 0:
        return {"error": "Total classes must be greater than zero."}
    if attended < 0 or attended > total:
        return {"error": f"Attended classes ({attended}) cannot be negative or exceed total classes ({total})."}

    current_pct = round((attended / total) * 100, 2)
    is_eligible = current_pct >= target_pct

    needed_classes = 0
    bunkable_classes = 0

    if current_pct < target_pct:
        # Solve for x: (attended + x) / (total + x) >= target_pct / 100
        # attended + x >= (target_pct / 100) * total + (target_pct / 100) * x
        # x * (1 - target_pct / 100) >= (target_pct / 100) * total - attended
        target_frac = target_pct / 100.0
        numerator = target_frac * total - attended
        denominator = 1.0 - target_frac
        if denominator > 0:
            needed_classes = math.ceil(numerator / denominator)
            if needed_classes < 0:
                needed_classes = 0
    else:
        # Solve for y: attended / (total + y) >= target_pct / 100
        # attended >= (target_pct / 100) * total + (target_pct / 100) * y
        # y * (target_pct / 100) <= attended - (target_pct / 100) * total
        target_frac = target_pct / 100.0
        max_total_allowed = math.floor(attended / target_frac)
        bunkable_classes = max_total_allowed - total
        if bunkable_classes < 0:
            bunkable_classes = 0

    return {
        "attended": attended,
        "total": total,
        "current_percentage": current_pct,
        "target_percentage": target_pct,
        "is_eligible": is_eligible,
        "status": "ELIGIBLE" if is_eligible else "SHORTAGE",
        "needed_classes_to_reach_target": needed_classes,
        "bunkable_classes_allowed": bunkable_classes,
    }


@tool
def calculate_attendance_tool(attended_classes: int, total_classes: int) -> str:
    """
    Use this tool to calculate class attendance percentage, attendance status, 
    how many consecutive classes the student MUST attend to reach 75% attendance requirement,
    or how many classes the student can safely bunk/miss while maintaining 75%.
    
    Args:
        attended_classes (int): The number of classes attended by the student.
        total_classes (int): The total number of classes conducted.
    """
    res = compute_attendance_stats(attended_classes, total_classes, target_pct=75.0)
    if "error" in res:
        return f"Error: {res['error']}"

    summary = (
        f"📊 **Attendance Summary**:\n"
        f"- **Classes Attended**: {res['attended']} out of {res['total']}\n"
        f"- **Current Attendance**: {res['current_percentage']}%\n"
        f"- **Requirement (75%)**: {'✅ ELIGIBLE' if res['is_eligible'] else '⚠️ SHORTAGE'}\n"
    )

    if res['is_eligible']:
        summary += (
            f"- **Bunking Allowance**: You can safely miss **{res['bunkable_classes_allowed']}** "
            f"more class(es) while keeping your attendance at or above 75%.\n"
        )
    else:
        summary += (
            f"- **Action Required**: You MUST attend the next **{res['needed_classes_to_reach_target']}** "
            f"consecutive class(es) without missing any to reach the 75% threshold.\n"
        )

    return summary
