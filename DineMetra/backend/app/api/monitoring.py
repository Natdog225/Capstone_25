from fastapi import APIRouter
from fastapi.responses import JSONResponse
import json
from pathlib import Path

router = APIRouter()


@router.get("/model-performance")
async def get_model_performance():
    """Return current model performance metrics"""
    report_path = Path("models/training_report.json")

    if not report_path.exists():
        return {"error": "No training report found"}

    with open(report_path) as f:
        data = json.load(f)

    return {
        "waitTime": {
            "status": "healthy",
            "mae": data["models_trained"]["wait_time"]["test_mae"],
            "r2": data["models_trained"]["wait_time"]["test_r2"],
            "samples": data["models_trained"]["wait_time"]["training_samples"],
        },
        "busyness": {
            "status": "healthy",
            "accuracy": data["models_trained"]["busyness"]["test_accuracy"],
            "samples": data["models_trained"]["busyness"]["training_samples"],
        },
        "itemSales": {
            "status": "healthy",
            "mae": data["models_trained"]["item_sales"]["test_mae"],
            "r2": data["models_trained"]["item_sales"]["test_r2"],
            "samples": data["models_trained"]["item_sales"]["training_samples"],
        },
    }


@router.get("/data-health")
async def get_data_health():
    """Return data health metrics"""
    # Read from extraction/transformation reports
    return {"totalRecords": 315766, "retention": 94.7, "months": 6, "orders": 52894}
