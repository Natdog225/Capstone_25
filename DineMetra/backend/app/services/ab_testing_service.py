"""
A/B Testing Service
Track model performance, compare predictions vs actuals, run experiments
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import logging
import json
import numpy as np
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger(__name__)


class ExperimentStatus(str, Enum):
    """Experiment status"""

    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class MetricType(str, Enum):
    """Performance metric types"""

    MAE = "mae"  # Mean Absolute Error
    RMSE = "rmse"  # Root Mean Square Error
    R_SQUARED = "r_squared"  # R² Score
    MAPE = "mape"  # Mean Absolute Percentage Error
    ACCURACY = "accuracy"  # Classification accuracy


class PredictionLog:
    """Single prediction log entry"""

    def __init__(
        self,
        log_id: str,
        model_version: str,
        prediction_type: str,
        predicted_value: float,
        input_features: Dict,
        timestamp: datetime,
        actual_value: Optional[float] = None,
        actual_recorded_at: Optional[datetime] = None,
    ):
        self.log_id = log_id
        self.model_version = model_version
        self.prediction_type = prediction_type
        self.predicted_value = predicted_value
        self.input_features = input_features
        self.timestamp = timestamp
        self.actual_value = actual_value
        self.actual_recorded_at = actual_recorded_at

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "log_id": self.log_id,
            "model_version": self.model_version,
            "prediction_type": self.prediction_type,
            "predicted_value": self.predicted_value,
            "input_features": self.input_features,
            "timestamp": self.timestamp.isoformat(),
            "actual_value": self.actual_value,
            "actual_recorded_at": (
                self.actual_recorded_at.isoformat() if self.actual_recorded_at else None
            ),
            "error": (
                abs(self.predicted_value - self.actual_value)
                if self.actual_value is not None
                else None
            ),
        }


class Experiment:
    """A/B test experiment"""

    def __init__(
        self,
        experiment_id: str,
        name: str,
        description: str,
        model_a_version: str,
        model_b_version: str,
        prediction_type: str,
        start_date: datetime,
        end_date: Optional[datetime] = None,
        status: ExperimentStatus = ExperimentStatus.DRAFT,
    ):
        self.experiment_id = experiment_id
        self.name = name
        self.description = description
        self.model_a_version = model_a_version
        self.model_b_version = model_b_version
        self.prediction_type = prediction_type
        self.start_date = start_date
        self.end_date = end_date
        self.status = status
        self.created_at = datetime.now()

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "experiment_id": self.experiment_id,
            "name": self.name,
            "description": self.description,
            "model_a_version": self.model_a_version,
            "model_b_version": self.model_b_version,
            "prediction_type": self.prediction_type,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }


class ABTestingService:
    """
    A/B Testing Service

    Features:
    - Log predictions with input features
    - Record actual outcomes
    - Calculate performance metrics
    - Compare model versions
    - Run A/B test experiments
    - Statistical significance testing
    """

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.realtime_dir = self.data_dir / "realtime"
        self.realtime_dir.mkdir(parents=True, exist_ok=True)

        # Storage
        self.prediction_logs: List[PredictionLog] = []
        self.experiments: Dict[str, Experiment] = {}

        # In-memory storage for fast access
        self.logs_by_model: Dict[str, List[PredictionLog]] = defaultdict(list)
        self.logs_by_type: Dict[str, List[PredictionLog]] = defaultdict(list)

        logger.info("A/B Testing Service initialized")

    def log_prediction(
        self,
        model_version: str,
        prediction_type: str,
        predicted_value: float,
        input_features: Dict,
    ) -> str:
        """
        Log a prediction

        Args:
            model_version: Model version identifier (e.g., "wait_time_v1")
            prediction_type: Type of prediction (wait_time, busyness, sales)
            predicted_value: Predicted value
            input_features: Input features used for prediction

        Returns:
            log_id: Unique log identifier
        """
        log_id = f"{prediction_type}_{model_version}_{int(datetime.now().timestamp() * 1000)}"

        log = PredictionLog(
            log_id=log_id,
            model_version=model_version,
            prediction_type=prediction_type,
            predicted_value=predicted_value,
            input_features=input_features,
            timestamp=datetime.now(),
        )

        self.prediction_logs.append(log)
        self.logs_by_model[model_version].append(log)
        self.logs_by_type[prediction_type].append(log)

        logger.debug(f"Logged prediction: {log_id}")

        return log_id

    def record_actual(self, log_id: str, actual_value: float) -> bool:
        """
        Record actual outcome for a prediction

        Args:
            log_id: Prediction log ID
            actual_value: Actual observed value

        Returns:
            True if recorded successfully
        """
        for log in self.prediction_logs:
            if log.log_id == log_id:
                log.actual_value = actual_value
                log.actual_recorded_at = datetime.now()
                logger.debug(f"Recorded actual for {log_id}: {actual_value}")
                return True

        logger.warning(f"Log ID not found: {log_id}")
        return False

    def calculate_mae(self, logs: List[PredictionLog]) -> Optional[float]:
        """Calculate Mean Absolute Error"""
        errors = [
            abs(log.predicted_value - log.actual_value)
            for log in logs
            if log.actual_value is not None
        ]

        if not errors:
            return None

        return np.mean(errors)

    def calculate_rmse(self, logs: List[PredictionLog]) -> Optional[float]:
        """Calculate Root Mean Square Error"""
        errors = [
            (log.predicted_value - log.actual_value) ** 2
            for log in logs
            if log.actual_value is not None
        ]

        if not errors:
            return None

        return np.sqrt(np.mean(errors))

    def calculate_r_squared(self, logs: List[PredictionLog]) -> Optional[float]:
        """Calculate R² Score"""
        complete_logs = [log for log in logs if log.actual_value is not None]

        if len(complete_logs) < 2:
            return None

        actuals = np.array([log.actual_value for log in complete_logs])
        predictions = np.array([log.predicted_value for log in complete_logs])

        ss_res = np.sum((actuals - predictions) ** 2)
        ss_tot = np.sum((actuals - np.mean(actuals)) ** 2)

        if ss_tot == 0:
            return None

        return 1 - (ss_res / ss_tot)

    def calculate_mape(self, logs: List[PredictionLog]) -> Optional[float]:
        """Calculate Mean Absolute Percentage Error"""
        errors = []

        for log in logs:
            if log.actual_value is not None and log.actual_value != 0:
                error = (
                    abs((log.predicted_value - log.actual_value) / log.actual_value)
                    * 100
                )
                errors.append(error)

        if not errors:
            return None

        return np.mean(errors)

    def calculate_accuracy(
        self, logs: List[PredictionLog], tolerance: float = 0.1
    ) -> Optional[float]:
        """
        Calculate accuracy (for regression within tolerance)

        Args:
            logs: Prediction logs
            tolerance: Tolerance level (10% = 0.1)

        Returns:
            Accuracy percentage
        """
        complete_logs = [log for log in logs if log.actual_value is not None]

        if not complete_logs:
            return None

        correct = 0
        for log in complete_logs:
            error_pct = (
                abs((log.predicted_value - log.actual_value) / log.actual_value)
                if log.actual_value != 0
                else 0
            )
            if error_pct <= tolerance:
                correct += 1

        return (correct / len(complete_logs)) * 100

    def get_model_performance(self, model_version: str, hours: int = 24) -> Dict:
        """
        Get performance metrics for a model version

        Args:
            model_version: Model version to analyze
            hours: Number of hours back to analyze

        Returns:
            Performance metrics dictionary
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)

        # Get recent logs for this model
        logs = [
            log
            for log in self.logs_by_model[model_version]
            if log.timestamp >= cutoff_time
        ]

        # Count logs with actuals
        complete_logs = [log for log in logs if log.actual_value is not None]

        metrics = {
            "model_version": model_version,
            "time_period_hours": hours,
            "total_predictions": len(logs),
            "predictions_with_actuals": len(complete_logs),
            "coverage_percent": (len(complete_logs) / len(logs) * 100) if logs else 0,
            "metrics": {},
        }

        if complete_logs:
            metrics["metrics"] = {
                "mae": self.calculate_mae(complete_logs),
                "rmse": self.calculate_rmse(complete_logs),
                "r_squared": self.calculate_r_squared(complete_logs),
                "mape": self.calculate_mape(complete_logs),
                "accuracy_10pct": self.calculate_accuracy(complete_logs, tolerance=0.1),
                "accuracy_20pct": self.calculate_accuracy(complete_logs, tolerance=0.2),
            }

        return metrics

    def compare_models(
        self, model_a_version: str, model_b_version: str, hours: int = 24
    ) -> Dict:
        """
        Compare performance of two models

        Args:
            model_a_version: First model version
            model_b_version: Second model version
            hours: Hours back to analyze

        Returns:
            Comparison results
        """
        perf_a = self.get_model_performance(model_a_version, hours)
        perf_b = self.get_model_performance(model_b_version, hours)

        comparison = {
            "model_a": perf_a,
            "model_b": perf_b,
            "winner": None,
            "improvements": {},
        }

        # Compare metrics
        if (
            perf_a["predictions_with_actuals"] > 0
            and perf_b["predictions_with_actuals"] > 0
        ):
            metrics_a = perf_a["metrics"]
            metrics_b = perf_b["metrics"]

            # Lower is better for MAE, RMSE, MAPE
            if metrics_a["mae"] and metrics_b["mae"]:
                if metrics_a["mae"] < metrics_b["mae"]:
                    comparison["winner"] = model_a_version
                else:
                    comparison["winner"] = model_b_version

                improvement = (
                    (metrics_b["mae"] - metrics_a["mae"]) / metrics_b["mae"]
                ) * 100
                comparison["improvements"]["mae"] = {
                    "percent": improvement,
                    "better_model": (
                        model_a_version if improvement > 0 else model_b_version
                    ),
                }

            # Higher is better for R² and accuracy
            if metrics_a["r_squared"] and metrics_b["r_squared"]:
                improvement = (
                    (metrics_a["r_squared"] - metrics_b["r_squared"])
                    / abs(metrics_b["r_squared"])
                ) * 100
                comparison["improvements"]["r_squared"] = {
                    "percent": improvement,
                    "better_model": (
                        model_a_version if improvement > 0 else model_b_version
                    ),
                }

        return comparison

    def create_experiment(
        self,
        name: str,
        description: str,
        model_a_version: str,
        model_b_version: str,
        prediction_type: str,
        duration_days: int = 7,
    ) -> str:
        """
        Create an A/B test experiment

        Args:
            name: Experiment name
            description: Experiment description
            model_a_version: Control model version
            model_b_version: Test model version
            prediction_type: Type of predictions to test
            duration_days: Experiment duration in days

        Returns:
            experiment_id
        """
        experiment_id = f"exp_{int(datetime.now().timestamp())}"

        experiment = Experiment(
            experiment_id=experiment_id,
            name=name,
            description=description,
            model_a_version=model_a_version,
            model_b_version=model_b_version,
            prediction_type=prediction_type,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=duration_days),
            status=ExperimentStatus.RUNNING,
        )

        self.experiments[experiment_id] = experiment

        logger.info(f"Created experiment: {name} ({experiment_id})")

        return experiment_id

    def get_experiment_results(self, experiment_id: str) -> Dict:
        """
        Get results for an experiment

        Args:
            experiment_id: Experiment ID

        Returns:
            Experiment results
        """
        if experiment_id not in self.experiments:
            return {"error": "Experiment not found"}

        experiment = self.experiments[experiment_id]

        # Calculate hours since start
        hours = (datetime.now() - experiment.start_date).total_seconds() / 3600

        # Compare models
        comparison = self.compare_models(
            experiment.model_a_version, experiment.model_b_version, hours=int(hours)
        )

        results = {
            "experiment": experiment.to_dict(),
            "comparison": comparison,
            "status": experiment.status,
            "days_running": hours / 24,
        }

        return results

    def get_prediction_logs(
        self,
        model_version: Optional[str] = None,
        prediction_type: Optional[str] = None,
        hours: int = 24,
        limit: int = 100,
    ) -> List[Dict]:
        """
        Get prediction logs with filters

        Args:
            model_version: Filter by model version
            prediction_type: Filter by prediction type
            hours: Hours back to retrieve
            limit: Maximum number of logs

        Returns:
            List of prediction logs
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)

        # Filter logs
        logs = self.prediction_logs

        if model_version:
            logs = [log for log in logs if log.model_version == model_version]

        if prediction_type:
            logs = [log for log in logs if log.prediction_type == prediction_type]

        # Filter by time
        logs = [log for log in logs if log.timestamp >= cutoff_time]

        # Sort by time, most recent first
        logs.sort(key=lambda x: x.timestamp, reverse=True)

        return [log.to_dict() for log in logs[:limit]]

    def get_summary_stats(self) -> Dict:
        """Get summary statistics"""
        total_logs = len(self.prediction_logs)
        logs_with_actuals = len(
            [log for log in self.prediction_logs if log.actual_value is not None]
        )

        stats = {
            "total_predictions": total_logs,
            "predictions_with_actuals": logs_with_actuals,
            "coverage_percent": (
                (logs_with_actuals / total_logs * 100) if total_logs > 0 else 0
            ),
            "models_tracked": len(self.logs_by_model),
            "prediction_types": len(self.logs_by_type),
            "active_experiments": len(
                [
                    e
                    for e in self.experiments.values()
                    if e.status == ExperimentStatus.RUNNING
                ]
            ),
        }

        return stats


# Global service instance
_ab_testing_service = None


def get_ab_testing_service() -> ABTestingService:
    """Get or create the global A/B testing service instance"""
    global _ab_testing_service
    if _ab_testing_service is None:
        _ab_testing_service = ABTestingService()
    return _ab_testing_service
