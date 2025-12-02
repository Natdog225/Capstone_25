"""
A/B Testing & Experiments API
Endpoints for managing experiments and tracking model performance
"""

from fastapi import APIRouter, Query, Body
from typing import Optional
import logging

from app.services.ab_testing_service import get_ab_testing_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/experiments", tags=["experiments"])


@router.post("/predictions/log")
async def log_prediction(
    model_version: str = Body(..., description="Model version identifier"),
    prediction_type: str = Body(
        ..., description="Type of prediction (wait_time, busyness, sales)"
    ),
    predicted_value: float = Body(..., description="Predicted value"),
    input_features: dict = Body(..., description="Input features used for prediction"),
):
    """
    Log a prediction for performance tracking

    Example:
    ```json
    {
      "model_version": "wait_time_v2",
      "prediction_type": "wait_time",
      "predicted_value": 28.5,
      "input_features": {
        "hour": 18,
        "day_of_week": 5,
        "weather": "sunny"
      }
    }
    ```
    """
    ab_service = get_ab_testing_service()

    log_id = ab_service.log_prediction(
        model_version=model_version,
        prediction_type=prediction_type,
        predicted_value=predicted_value,
        input_features=input_features,
    )

    return {
        "success": True,
        "log_id": log_id,
        "message": "Prediction logged successfully",
    }


@router.post("/predictions/{log_id}/actual")
async def record_actual_value(
    log_id: str, actual_value: float = Body(..., description="Actual observed value")
):
    """
    Record actual outcome for a prediction

    This allows tracking accuracy by comparing predictions to reality

    Example:
    ```json
    {
      "actual_value": 32.0
    }
    ```
    """
    ab_service = get_ab_testing_service()

    success = ab_service.record_actual(log_id, actual_value)

    if success:
        return {"success": True, "message": f"Actual value recorded for {log_id}"}
    else:
        return {"success": False, "error": "Log ID not found"}


@router.get("/predictions/logs")
async def get_prediction_logs(
    model_version: Optional[str] = Query(None, description="Filter by model version"),
    prediction_type: Optional[str] = Query(
        None, description="Filter by prediction type"
    ),
    hours: int = Query(24, ge=1, le=168, description="Hours back to retrieve (1-168)"),
    limit: int = Query(100, ge=1, le=1000, description="Max number of logs (1-1000)"),
):
    """
    Get prediction logs with optional filters

    Example:
    ```
    GET /api/experiments/predictions/logs?model_version=wait_time_v2&hours=24
    ```
    """
    ab_service = get_ab_testing_service()

    logs = ab_service.get_prediction_logs(
        model_version=model_version,
        prediction_type=prediction_type,
        hours=hours,
        limit=limit,
    )

    return {"success": True, "count": len(logs), "logs": logs}


@router.get("/models/{model_version}/performance")
async def get_model_performance(
    model_version: str,
    hours: int = Query(24, ge=1, le=168, description="Hours back to analyze"),
):
    """
    Get performance metrics for a specific model version

    Returns MAE, RMSE, R², MAPE, and accuracy metrics

    Example:
    ```
    GET /api/experiments/models/wait_time_v2/performance?hours=24
    ```
    """
    ab_service = get_ab_testing_service()

    performance = ab_service.get_model_performance(
        model_version=model_version, hours=hours
    )

    return {"success": True, "performance": performance}


@router.get("/models/compare")
async def compare_models(
    model_a: str = Query(..., description="First model version"),
    model_b: str = Query(..., description="Second model version"),
    hours: int = Query(24, ge=1, le=168, description="Hours back to analyze"),
):
    """
    Compare performance of two model versions

    Returns side-by-side comparison with winner determination

    Example:
    ```
    GET /api/experiments/models/compare?model_a=wait_time_v1&model_b=wait_time_v2&hours=168
    ```
    """
    ab_service = get_ab_testing_service()

    comparison = ab_service.compare_models(
        model_a_version=model_a, model_b_version=model_b, hours=hours
    )

    return {"success": True, "comparison": comparison}


@router.post("/experiments/create")
async def create_experiment(
    name: str = Body(..., description="Experiment name"),
    description: str = Body(..., description="Experiment description"),
    model_a_version: str = Body(..., description="Control model version"),
    model_b_version: str = Body(..., description="Test model version"),
    prediction_type: str = Body(..., description="Type of predictions to test"),
    duration_days: int = Body(
        7, ge=1, le=90, description="Experiment duration in days"
    ),
):
    """
    Create a new A/B test experiment

    Example:
    ```json
    {
      "name": "Wait Time Model V2 Test",
      "description": "Testing new weather-aware wait time model",
      "model_a_version": "wait_time_v1",
      "model_b_version": "wait_time_v2",
      "prediction_type": "wait_time",
      "duration_days": 14
    }
    ```
    """
    ab_service = get_ab_testing_service()

    experiment_id = ab_service.create_experiment(
        name=name,
        description=description,
        model_a_version=model_a_version,
        model_b_version=model_b_version,
        prediction_type=prediction_type,
        duration_days=duration_days,
    )

    return {
        "success": True,
        "experiment_id": experiment_id,
        "message": f"Experiment created: {name}",
    }


@router.get("/experiments/{experiment_id}")
async def get_experiment_results(experiment_id: str):
    """
    Get results for an experiment

    Returns comparison of both model versions with statistical metrics

    Example:
    ```
    GET /api/experiments/experiments/exp_1234567890
    ```
    """
    ab_service = get_ab_testing_service()

    results = ab_service.get_experiment_results(experiment_id)

    if "error" in results:
        return {"success": False, "error": results["error"]}

    return {"success": True, "results": results}


@router.get("/experiments")
async def list_experiments():
    """
    List all experiments

    Returns list of all experiments with their status
    """
    ab_service = get_ab_testing_service()

    experiments = [exp.to_dict() for exp in ab_service.experiments.values()]

    return {"success": True, "count": len(experiments), "experiments": experiments}


@router.get("/stats")
async def get_ab_testing_stats():
    """
    Get overall A/B testing statistics

    Returns summary of all tracked predictions and experiments
    """
    ab_service = get_ab_testing_service()

    stats = ab_service.get_summary_stats()

    return {"success": True, "stats": stats}
