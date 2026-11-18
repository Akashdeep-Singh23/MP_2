from fastapi import APIRouter
import json
import os

router = APIRouter()

@router.get("/nutrition", summary="Get General Nutrition Guidance")
async def get_nutrition():
    """
    Returns general, non-medical educational nutrition guidance (NUT-01 to NUT-07).
    """
    path = os.path.join(os.path.dirname(__file__), "..", "..", "content", "nutrition.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception:
        return {
            "disclaimer": "This guidance is for general educational purposes only.",
            "topics": []
        }
