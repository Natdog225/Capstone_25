"""
Dinemetra Model Monitoring System
Tracks model performance over time and detects degradation

This script:
1. Logs predictions and actual outcomes
2. Calculates rolling accuracy metrics
3. Detects model drift/degradation
4. Generates performance reports
5. Triggers retraining when needed

Run: python scripts/monitor_models.py
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import json
import logging
import pickle
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ModelMonitor:
    """
    Monitors ML model performance and detects degradation
    """

    def __init__(self, models_dir: str = "models", logs_dir: str = "logs"):
        """
        Initialize monitor

        Args:
            models_dir: Directory containing trained models
            logs_dir: Directory for prediction logs and monitoring data
        """
        self.models_dir = Path(models_dir)
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(exist_ok=True)

        self.prediction_log_path = self.logs_dir / "predictions.jsonl"
        self.metrics_log_path = self.logs_dir / "metrics.jsonl"
        self.monitoring_report_path = self.logs_dir / "monitoring_report.json"

        # Performance thresholds for alerts
        self.thresholds = {
            "wait_time": {
                "mae_warning": 6.0,  # minutes
                "mae_critical": 8.0,
                "r2_warning": 0.75,
                "r2_critical": 0.65,
            },
            "busyness": {"accuracy_warning": 0.80, "accuracy_critical": 0.70},
            "item_sales": {
                "mae_warning": 12.0,  # units
                "mae_critical": 15.0,
                "r2_warning": 0.60,
                "r2_critical": 0.50,
            },
        }

    # ========================================
    # PREDICTION LOGGING
    # ========================================

    def log_prediction(self, model_name: str, prediction: Dict, actual: float = None):
        """
        Log a prediction (and actual outcome if available)

        Args:
            model_name: Name of model (wait_time, busyness, item_sales)
            prediction: Prediction dictionary with features and prediction
            actual: Actual outcome (if known)
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "model": model_name,
            "prediction": prediction,
            "actual": actual,
        }

        # Append to log file
        with open(self.prediction_log_path, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

    def load_prediction_logs(self, days: int = 30) -> pd.DataFrame:
        """
        Load prediction logs from the last N days

        Args:
            days: Number of days to load

        Returns:
            DataFrame with prediction logs
        """
        if not self.prediction_log_path.exists():
            logger.warning("No prediction logs found")
            return pd.DataFrame()

        # Read JSONL file
        logs = []
        with open(self.prediction_log_path, "r") as f:
            for line in f:
                try:
                    logs.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        if not logs:
            return pd.DataFrame()

        df = pd.DataFrame(logs)
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # Filter to last N days
        cutoff = datetime.now() - timedelta(days=days)
        df = df[df["timestamp"] >= cutoff]

        return df

    # ========================================
    # PERFORMANCE ANALYSIS
    # ========================================

    def analyze_wait_time_performance(self, logs_df: pd.DataFrame) -> Dict:
        """
        Analyze wait time model performance

        Args:
            logs_df: DataFrame with prediction logs

        Returns:
            Dictionary with performance metrics
        """
        logger.info("📊 Analyzing wait time model performance...")

        # Filter for wait_time model with actual values
        df = logs_df[
            (logs_df["model"] == "wait_time") & (logs_df["actual"].notna())
        ].copy()

        if len(df) == 0:
            logger.warning("No wait time predictions with actuals found")
            return {"status": "no_data", "sample_size": 0}

        # Extract predictions and actuals
        df["predicted"] = df["prediction"].apply(
            lambda x: x.get("predicted_wait_minutes", 0)
        )
        df["actual"] = df["actual"].astype(float)

        # Calculate metrics
        mae = np.mean(np.abs(df["predicted"] - df["actual"]))
        rmse = np.sqrt(np.mean((df["predicted"] - df["actual"]) ** 2))

        # R² score
        ss_res = np.sum((df["actual"] - df["predicted"]) ** 2)
        ss_tot = np.sum((df["actual"] - df["actual"].mean()) ** 2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        # Within-threshold accuracy (predictions within 5 minutes)
        within_5min = (np.abs(df["predicted"] - df["actual"]) <= 5).mean() * 100

        # Calculate rolling metrics (last 7 days vs previous 7 days)
        midpoint = len(df) // 2
        recent_mae = np.mean(
            np.abs(df["predicted"].iloc[midpoint:] - df["actual"].iloc[midpoint:])
        )
        previous_mae = np.mean(
            np.abs(df["predicted"].iloc[:midpoint] - df["actual"].iloc[:midpoint])
        )

        performance_trend = "improving" if recent_mae < previous_mae else "degrading"

        # Check thresholds
        status = "healthy"
        if (
            mae > self.thresholds["wait_time"]["mae_critical"]
            or r2 < self.thresholds["wait_time"]["r2_critical"]
        ):
            status = "critical"
        elif (
            mae > self.thresholds["wait_time"]["mae_warning"]
            or r2 < self.thresholds["wait_time"]["r2_warning"]
        ):
            status = "warning"

        metrics = {
            "status": status,
            "sample_size": len(df),
            "mae": float(mae),
            "rmse": float(rmse),
            "r2": float(r2),
            "within_5min_pct": float(within_5min),
            "recent_mae": float(recent_mae),
            "previous_mae": float(previous_mae),
            "trend": performance_trend,
            "last_updated": datetime.now().isoformat(),
        }

        logger.info(f"   MAE: {mae:.2f} minutes (Status: {status})")
        logger.info(f"   R²: {r2:.3f}")
        logger.info(f"   Within 5 min: {within_5min:.1f}%")
        logger.info(f"   Trend: {performance_trend}")

        return metrics

    def analyze_busyness_performance(self, logs_df: pd.DataFrame) -> Dict:
        """
        Analyze busyness model performance

        Args:
            logs_df: DataFrame with prediction logs

        Returns:
            Dictionary with performance metrics
        """
        logger.info("📊 Analyzing busyness model performance...")

        # Filter for busyness model with actual values
        df = logs_df[
            (logs_df["model"] == "busyness") & (logs_df["actual"].notna())
        ].copy()

        if len(df) == 0:
            logger.warning("No busyness predictions with actuals found")
            return {"status": "no_data", "sample_size": 0}

        # Extract predictions and actuals
        df["predicted"] = df["prediction"].apply(lambda x: x.get("level", "moderate"))
        df["actual"] = df["actual"].astype(str)

        # Calculate accuracy
        accuracy = (df["predicted"] == df["actual"]).mean()

        # Per-class accuracy
        class_accuracy = {}
        for level in ["slow", "moderate", "peak"]:
            mask = df["actual"] == level
            if mask.sum() > 0:
                class_accuracy[level] = (
                    df[mask]["predicted"] == df[mask]["actual"]
                ).mean()

        # Check thresholds
        status = "healthy"
        if accuracy < self.thresholds["busyness"]["accuracy_critical"]:
            status = "critical"
        elif accuracy < self.thresholds["busyness"]["accuracy_warning"]:
            status = "warning"

        metrics = {
            "status": status,
            "sample_size": len(df),
            "accuracy": float(accuracy),
            "class_accuracy": {k: float(v) for k, v in class_accuracy.items()},
            "last_updated": datetime.now().isoformat(),
        }

        logger.info(f"   Accuracy: {accuracy:.3f} (Status: {status})")
        for level, acc in class_accuracy.items():
            logger.info(f"   {level.capitalize()}: {acc:.3f}")

        return metrics

    def analyze_item_sales_performance(self, logs_df: pd.DataFrame) -> Dict:
        """
        Analyze item sales model performance

        Args:
            logs_df: DataFrame with prediction logs

        Returns:
            Dictionary with performance metrics
        """
        logger.info("📊 Analyzing item sales model performance...")

        # Filter for item_sales model with actual values
        df = logs_df[
            (logs_df["model"] == "item_sales") & (logs_df["actual"].notna())
        ].copy()

        if len(df) == 0:
            logger.warning("No item sales predictions with actuals found")
            return {"status": "no_data", "sample_size": 0}

        # Extract predictions and actuals
        df["predicted"] = df["prediction"].apply(
            lambda x: x.get("predicted_quantity", 0)
        )
        df["actual"] = df["actual"].astype(float)

        # Calculate metrics
        mae = np.mean(np.abs(df["predicted"] - df["actual"]))
        rmse = np.sqrt(np.mean((df["predicted"] - df["actual"]) ** 2))

        # R² score
        ss_res = np.sum((df["actual"] - df["predicted"]) ** 2)
        ss_tot = np.sum((df["actual"] - df["actual"].mean()) ** 2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        # Check thresholds
        status = "healthy"
        if (
            mae > self.thresholds["item_sales"]["mae_critical"]
            or r2 < self.thresholds["item_sales"]["r2_critical"]
        ):
            status = "critical"
        elif (
            mae > self.thresholds["item_sales"]["mae_warning"]
            or r2 < self.thresholds["item_sales"]["r2_warning"]
        ):
            status = "warning"

        metrics = {
            "status": status,
            "sample_size": len(df),
            "mae": float(mae),
            "rmse": float(rmse),
            "r2": float(r2),
            "last_updated": datetime.now().isoformat(),
        }

        logger.info(f"   MAE: {mae:.2f} units (Status: {status})")
        logger.info(f"   R²: {r2:.3f}")

        return metrics

    # ========================================
    # MONITORING DASHBOARD
    # ========================================

    def generate_monitoring_report(self, days: int = 30) -> Dict:
        """
        Generate comprehensive monitoring report

        Args:
            days: Number of days to analyze

        Returns:
            Dictionary with monitoring report
        """
        logger.info(f"📈 Generating monitoring report (last {days} days)...")

        # Load prediction logs
        logs_df = self.load_prediction_logs(days=days)

        if logs_df.empty:
            logger.warning("No prediction logs available for analysis")
            return {"status": "no_data", "message": "No predictions logged yet"}

        # Analyze each model
        wait_time_metrics = self.analyze_wait_time_performance(logs_df)
        busyness_metrics = self.analyze_busyness_performance(logs_df)
        item_sales_metrics = self.analyze_item_sales_performance(logs_df)

        # Determine overall system status
        statuses = [
            wait_time_metrics.get("status", "unknown"),
            busyness_metrics.get("status", "unknown"),
            item_sales_metrics.get("status", "unknown"),
        ]

        if "critical" in statuses:
            overall_status = "critical"
        elif "warning" in statuses:
            overall_status = "warning"
        elif "no_data" in statuses:
            overall_status = "partial_data"
        else:
            overall_status = "healthy"

        # Compile report
        report = {
            "generated_at": datetime.now().isoformat(),
            "period_days": days,
            "overall_status": overall_status,
            "models": {
                "wait_time": wait_time_metrics,
                "busyness": busyness_metrics,
                "item_sales": item_sales_metrics,
            },
            "recommendations": self._generate_recommendations(
                wait_time_metrics, busyness_metrics, item_sales_metrics
            ),
        }

        # Save report
        with open(self.monitoring_report_path, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"\n✓ Monitoring report saved to: {self.monitoring_report_path}")
        logger.info(f"📊 Overall Status: {overall_status.upper()}")

        return report

    def _generate_recommendations(
        self, wait_time: Dict, busyness: Dict, item_sales: Dict
    ) -> List[str]:
        """Generate actionable recommendations based on metrics"""
        recommendations = []

        # Wait time model
        if wait_time.get("status") == "critical":
            recommendations.append(
                "⚠️ CRITICAL: Wait time model requires immediate retraining"
            )
        elif wait_time.get("status") == "warning":
            recommendations.append(
                "⚠️ Wait time model showing degradation - schedule retraining"
            )

        if wait_time.get("trend") == "degrading":
            recommendations.append("📉 Wait time predictions degrading over time")

        # Busyness model
        if busyness.get("status") == "critical":
            recommendations.append(
                "⚠️ CRITICAL: Busyness model requires immediate retraining"
            )
        elif busyness.get("status") == "warning":
            recommendations.append(
                "⚠️ Busyness model showing degradation - schedule retraining"
            )

        # Item sales model
        if item_sales.get("status") == "critical":
            recommendations.append(
                "⚠️ CRITICAL: Item sales model requires immediate retraining"
            )
        elif item_sales.get("status") == "warning":
            recommendations.append(
                "⚠️ Item sales model showing degradation - schedule retraining"
            )

        # General recommendations
        if not recommendations:
            recommendations.append(
                "✅ All models performing well - maintain current monitoring schedule"
            )

        if any(
            m.get("sample_size", 0) < 100 for m in [wait_time, busyness, item_sales]
        ):
            recommendations.append(
                "ℹ️ Low sample size - ensure predictions are being logged consistently"
            )

        return recommendations

    # ========================================
    # VISUALIZATION
    # ========================================

    def plot_performance_trends(self, days: int = 30):
        """
        Generate performance trend visualizations

        Args:
            days: Number of days to plot
        """
        logger.info("📊 Generating performance visualizations...")

        logs_df = self.load_prediction_logs(days=days)

        if logs_df.empty:
            logger.warning("No data to visualize")
            return

        # Create figure with subplots
        fig, axes = plt.subplots(3, 1, figsize=(12, 10))
        fig.suptitle(
            f"Dinemetra Model Performance - Last {days} Days",
            fontsize=16,
            fontweight="bold",
        )

        # Plot 1: Wait Time Model
        wait_df = logs_df[
            (logs_df["model"] == "wait_time") & (logs_df["actual"].notna())
        ].copy()

        if not wait_df.empty:
            wait_df["predicted"] = wait_df["prediction"].apply(
                lambda x: x.get("predicted_wait_minutes", 0)
            )
            wait_df["actual"] = wait_df["actual"].astype(float)
            wait_df["error"] = np.abs(wait_df["predicted"] - wait_df["actual"])

            # Rolling MAE
            wait_df = wait_df.sort_values("timestamp")
            wait_df["rolling_mae"] = (
                wait_df["error"].rolling(window=50, min_periods=10).mean()
            )

            axes[0].plot(wait_df["timestamp"], wait_df["rolling_mae"], linewidth=2)
            axes[0].axhline(
                y=self.thresholds["wait_time"]["mae_warning"],
                color="orange",
                linestyle="--",
                label="Warning Threshold",
            )
            axes[0].axhline(
                y=self.thresholds["wait_time"]["mae_critical"],
                color="red",
                linestyle="--",
                label="Critical Threshold",
            )
            axes[0].set_ylabel("MAE (minutes)")
            axes[0].set_title("Wait Time Model - Rolling MAE")
            axes[0].legend()
            axes[0].grid(True, alpha=0.3)

        # Plot 2: Busyness Model Accuracy
        busy_df = logs_df[
            (logs_df["model"] == "busyness") & (logs_df["actual"].notna())
        ].copy()

        if not busy_df.empty:
            busy_df["predicted"] = busy_df["prediction"].apply(
                lambda x: x.get("level", "moderate")
            )
            busy_df["actual"] = busy_df["actual"].astype(str)
            busy_df["correct"] = (busy_df["predicted"] == busy_df["actual"]).astype(int)

            # Rolling accuracy
            busy_df = busy_df.sort_values("timestamp")
            busy_df["rolling_accuracy"] = (
                busy_df["correct"].rolling(window=50, min_periods=10).mean()
            )

            axes[1].plot(busy_df["timestamp"], busy_df["rolling_accuracy"], linewidth=2)
            axes[1].axhline(
                y=self.thresholds["busyness"]["accuracy_warning"],
                color="orange",
                linestyle="--",
                label="Warning Threshold",
            )
            axes[1].axhline(
                y=self.thresholds["busyness"]["accuracy_critical"],
                color="red",
                linestyle="--",
                label="Critical Threshold",
            )
            axes[1].set_ylabel("Accuracy")
            axes[1].set_title("Busyness Model - Rolling Accuracy")
            axes[1].legend()
            axes[1].grid(True, alpha=0.3)

        # Plot 3: Item Sales Model
        sales_df = logs_df[
            (logs_df["model"] == "item_sales") & (logs_df["actual"].notna())
        ].copy()

        if not sales_df.empty:
            sales_df["predicted"] = sales_df["prediction"].apply(
                lambda x: x.get("predicted_quantity", 0)
            )
            sales_df["actual"] = sales_df["actual"].astype(float)
            sales_df["error"] = np.abs(sales_df["predicted"] - sales_df["actual"])

            # Rolling MAE
            sales_df = sales_df.sort_values("timestamp")
            sales_df["rolling_mae"] = (
                sales_df["error"].rolling(window=50, min_periods=10).mean()
            )

            axes[2].plot(sales_df["timestamp"], sales_df["rolling_mae"], linewidth=2)
            axes[2].axhline(
                y=self.thresholds["item_sales"]["mae_warning"],
                color="orange",
                linestyle="--",
                label="Warning Threshold",
            )
            axes[2].axhline(
                y=self.thresholds["item_sales"]["mae_critical"],
                color="red",
                linestyle="--",
                label="Critical Threshold",
            )
            axes[2].set_ylabel("MAE (units)")
            axes[2].set_title("Item Sales Model - Rolling MAE")
            axes[2].set_xlabel("Date")
            axes[2].legend()
            axes[2].grid(True, alpha=0.3)

        # Format x-axis
        for ax in axes:
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, days // 10)))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

        plt.tight_layout()

        # Save plot
        plot_path = self.logs_dir / "performance_trends.png"
        plt.savefig(plot_path, dpi=150, bbox_inches="tight")
        logger.info(f"✓ Performance plots saved to: {plot_path}")

        plt.close()


# ========================================
# MAIN EXECUTION
# ========================================


def main():
    """Main monitoring function"""
    try:
        monitor = ModelMonitor(models_dir="models", logs_dir="logs")

        # Generate monitoring report
        report = monitor.generate_monitoring_report(days=30)

        # Generate visualizations (requires matplotlib)
        try:
            monitor.plot_performance_trends(days=30)
        except Exception as e:
            logger.warning(f"Could not generate plots: {e}")

        # Print recommendations
        if report.get("recommendations"):
            logger.info("\n📋 RECOMMENDATIONS:")
            for rec in report["recommendations"]:
                logger.info(f"   {rec}")

        logger.info("\n✅ Monitoring complete!")

    except Exception as e:
        logger.error(f"❌ Monitoring failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
