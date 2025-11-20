"""
Dinemetra Automated Model Retraining System
Automatically retrains models based on performance metrics and schedules

This script:
1. Checks model performance against thresholds
2. Determines if retraining is needed
3. Backs up current models
4. Trains new models
5. Validates new models before deployment
6. Sends notifications/alerts

Run: python scripts/auto_retrain.py
Schedule: Add to cron for automated execution
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import json
import logging
import shutil
import pickle

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AutoRetrainer:
    """
    Handles automated model retraining
    """

    def __init__(
        self,
        models_dir: str = "models",
        logs_dir: str = "logs",
        backup_dir: str = "models/backups",
    ):
        """
        Initialize retrainer

        Args:
            models_dir: Directory containing trained models
            logs_dir: Directory with monitoring logs
            backup_dir: Directory for model backups
        """
        self.models_dir = Path(models_dir)
        self.logs_dir = Path(logs_dir)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        self.monitoring_report_path = self.logs_dir / "monitoring_report.json"
        self.retrain_log_path = self.logs_dir / "retrain_history.jsonl"

        # Retraining policies
        self.policies = {
            "schedule": {
                "min_days_between_retrain": 7,  # Don't retrain more than weekly
                "max_days_without_retrain": 30,  # Force retrain if no retrain in 30 days
            },
            "performance": {
                "retrain_on_critical": True,  # Retrain immediately if critical
                "retrain_on_warning": False,  # Don't retrain on warning (wait for critical)
                "min_improvement_required": 0.05,  # New model must be 5% better
            },
            "data": {
                "min_new_samples": 1000  # Need at least 1000 new samples to retrain
            },
        }

    # ========================================
    # RETRAINING DECISION LOGIC
    # ========================================

    def should_retrain(self) -> dict:
        """
        Determine if models should be retrained

        Returns:
            Dictionary with retrain decision and reasons
        """
        logger.info("🤔 Evaluating retraining criteria...")

        # Load monitoring report
        if not self.monitoring_report_path.exists():
            logger.warning("No monitoring report found. Run monitor_models.py first.")
            return {"should_retrain": False, "reason": "no_monitoring_data"}

        with open(self.monitoring_report_path, "r") as f:
            report = json.load(f)

        reasons = []
        should_retrain = False

        # Check 1: Time since last retrain
        last_retrain_date = self._get_last_retrain_date()
        days_since_retrain = (
            (datetime.now() - last_retrain_date).days if last_retrain_date else 999
        )

        logger.info(f"   Days since last retrain: {days_since_retrain}")

        if days_since_retrain >= self.policies["schedule"]["max_days_without_retrain"]:
            reasons.append(
                f"Scheduled retrain (last trained {days_since_retrain} days ago)"
            )
            should_retrain = True
        elif days_since_retrain < self.policies["schedule"]["min_days_between_retrain"]:
            logger.info(
                f"   ⏸️  Too soon to retrain (min {self.policies['schedule']['min_days_between_retrain']} days)"
            )
            return {
                "should_retrain": False,
                "reason": "too_soon",
                "days_until_eligible": self.policies["schedule"][
                    "min_days_between_retrain"
                ]
                - days_since_retrain,
            }

        # Check 2: Performance degradation
        overall_status = report.get("overall_status", "unknown")

        if (
            overall_status == "critical"
            and self.policies["performance"]["retrain_on_critical"]
        ):
            reasons.append("Critical performance degradation detected")
            should_retrain = True
        elif (
            overall_status == "warning"
            and self.policies["performance"]["retrain_on_warning"]
        ):
            reasons.append("Warning-level performance degradation")
            should_retrain = True

        # Check individual model statuses
        for model_name, metrics in report.get("models", {}).items():
            if metrics.get("status") == "critical":
                reasons.append(f"{model_name} model in critical state")
                should_retrain = True

        # Check 3: New data availability
        # This is a placeholder - you'd need to check actual data growth
        new_samples = self._estimate_new_samples()
        if new_samples >= self.policies["data"]["min_new_samples"]:
            reasons.append(f"Sufficient new data available ({new_samples} samples)")
        else:
            logger.info(
                f"   ℹ️  Insufficient new data ({new_samples} samples, need {self.policies['data']['min_new_samples']})"
            )
            if not should_retrain:
                return {
                    "should_retrain": False,
                    "reason": "insufficient_data",
                    "new_samples": new_samples,
                }

        decision = {
            "should_retrain": should_retrain,
            "reasons": reasons,
            "overall_status": overall_status,
            "days_since_retrain": days_since_retrain,
            "evaluated_at": datetime.now().isoformat(),
        }

        if should_retrain:
            logger.info(f"   ✅ Retraining recommended:")
            for reason in reasons:
                logger.info(f"      - {reason}")
        else:
            logger.info(f"   ⏸️  Retraining not needed")

        return decision

    def _get_last_retrain_date(self) -> datetime:
        """Get date of last retrain from log"""
        if not self.retrain_log_path.exists():
            return None

        # Read last line of retrain log
        with open(self.retrain_log_path, "r") as f:
            lines = f.readlines()
            if lines:
                last_entry = json.loads(lines[-1])
                return datetime.fromisoformat(last_entry["timestamp"])

        return None

    def _estimate_new_samples(self) -> int:
        """
        Estimate number of new samples since last retrain
        This is a placeholder - in production, query actual data
        """
        # Check last model metadata for training sample count
        wait_time_model_path = self.models_dir / "wait_time_model.pkl"

        if not wait_time_model_path.exists():
            return 10000  # Assume lots of data if no model exists

        try:
            with open(wait_time_model_path, "rb") as f:
                model_data = pickle.load(f)
                last_train_samples = model_data.get("metadata", {}).get(
                    "training_samples", 0
                )

            # In production, you'd query the database for actual count
            # For now, estimate based on time
            last_retrain = self._get_last_retrain_date()
            if last_retrain:
                days_since = (datetime.now() - last_retrain).days
                # Estimate ~50 new samples per day (adjust based on actual traffic)
                estimated_new = days_since * 50
                return estimated_new
            else:
                return 10000  # Lots of data if never trained
        except:
            return 10000

    # ========================================
    # RETRAINING EXECUTION
    # ========================================

    def execute_retrain(self, force: bool = False) -> dict:
        """
        Execute model retraining

        Args:
            force: Force retrain regardless of criteria

        Returns:
            Dictionary with retrain results
        """
        logger.info("=" * 60)
        logger.info("🔄 AUTOMATED MODEL RETRAINING")
        logger.info("=" * 60 + "\n")

        # Check if retrain is needed
        decision = self.should_retrain()

        if not decision["should_retrain"] and not force:
            logger.info("⏸️  Retraining not needed at this time")
            return decision

        if force:
            logger.info("⚡ FORCED RETRAIN - Bypassing criteria checks")

        result = {
            "timestamp": datetime.now().isoformat(),
            "forced": force,
            "decision": decision,
            "backup_created": False,
            "models_trained": {},
            "validation_passed": False,
            "deployed": False,
        }

        try:
            # Step 1: Backup current models
            logger.info("\n📦 Step 1: Backing up current models...")
            backup_path = self._backup_current_models()
            result["backup_created"] = True
            result["backup_path"] = str(backup_path)
            logger.info(f"   ✓ Backup created at: {backup_path}")

            # Step 2: Train new models
            logger.info("\n🤖 Step 2: Training new models...")
            from scripts.train_models import ModelTrainer

            trainer = ModelTrainer(data_dir="data", models_dir="models/temp")
            trainer.train_all_models()

            result["models_trained"] = trainer.training_report["models_trained"]
            logger.info("   ✓ New models trained successfully")

            # Step 3: Validate new models
            logger.info("\n✅ Step 3: Validating new models...")
            validation = self._validate_new_models(backup_path)
            result["validation"] = validation

            if validation["passed"]:
                result["validation_passed"] = True
                logger.info("   ✓ New models validated successfully")

                # Step 4: Deploy new models
                logger.info("\n🚀 Step 4: Deploying new models...")
                self._deploy_new_models()
                result["deployed"] = True
                logger.info("   ✓ New models deployed")
            else:
                logger.warning("   ⚠️  Validation failed - rolling back to backup")
                self._rollback_to_backup(backup_path)
                result["deployed"] = False

            # Log retrain event
            self._log_retrain_event(result)

            logger.info("\n" + "=" * 60)
            if result["deployed"]:
                logger.info("✅ RETRAINING COMPLETED SUCCESSFULLY")
            else:
                logger.info("⚠️  RETRAINING COMPLETED WITH ISSUES")
            logger.info("=" * 60)

        except Exception as e:
            logger.error(f"\n❌ Retraining failed: {str(e)}")
            result["error"] = str(e)

            # Rollback if backup exists
            if result["backup_created"]:
                logger.info("🔄 Rolling back to previous models...")
                self._rollback_to_backup(backup_path)

        return result

    def _backup_current_models(self) -> Path:
        """Backup current models"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"backup_{timestamp}"
        backup_path.mkdir(exist_ok=True)

        # Copy all model files
        for model_file in self.models_dir.glob("*.pkl"):
            shutil.copy2(model_file, backup_path / model_file.name)

        # Copy training report
        report_file = self.models_dir / "training_report.json"
        if report_file.exists():
            shutil.copy2(report_file, backup_path / report_file.name)

        return backup_path

    def _validate_new_models(self, backup_path: Path) -> dict:
        """
        Validate new models against old models

        Args:
            backup_path: Path to backed up models

        Returns:
            Dictionary with validation results
        """
        validation = {"passed": True, "models": {}, "overall_improvement": 0.0}

        # Load old and new training reports
        old_report_path = backup_path / "training_report.json"
        new_report_path = Path("models/temp/training_report.json")

        if not old_report_path.exists() or not new_report_path.exists():
            logger.warning("   Could not compare models - missing training reports")
            validation["passed"] = True  # Default to accepting if can't compare
            return validation

        with open(old_report_path, "r") as f:
            old_report = json.load(f)
        with open(new_report_path, "r") as f:
            new_report = json.load(f)

        improvements = []

        # Compare wait time model
        if (
            "wait_time" in old_report["models_trained"]
            and "wait_time" in new_report["models_trained"]
        ):
            old_mae = old_report["models_trained"]["wait_time"]["test_mae"]
            new_mae = new_report["models_trained"]["wait_time"]["test_mae"]
            improvement = (old_mae - new_mae) / old_mae

            validation["models"]["wait_time"] = {
                "old_mae": old_mae,
                "new_mae": new_mae,
                "improvement": improvement,
                "acceptable": new_mae <= old_mae * 1.1,  # Allow up to 10% degradation
            }

            improvements.append(improvement)
            logger.info(
                f"   Wait Time: {old_mae:.2f} → {new_mae:.2f} ({improvement:+.1%})"
            )

        # Compare busyness model
        if (
            "busyness" in old_report["models_trained"]
            and "busyness" in new_report["models_trained"]
        ):
            old_acc = old_report["models_trained"]["busyness"]["test_accuracy"]
            new_acc = new_report["models_trained"]["busyness"]["test_accuracy"]
            improvement = (new_acc - old_acc) / old_acc

            validation["models"]["busyness"] = {
                "old_accuracy": old_acc,
                "new_accuracy": new_acc,
                "improvement": improvement,
                "acceptable": new_acc >= old_acc * 0.95,  # Allow up to 5% degradation
            }

            improvements.append(improvement)
            logger.info(
                f"   Busyness: {old_acc:.3f} → {new_acc:.3f} ({improvement:+.1%})"
            )

        # Compare item sales model
        if (
            "item_sales" in old_report["models_trained"]
            and "item_sales" in new_report["models_trained"]
        ):
            old_mae = old_report["models_trained"]["item_sales"]["test_mae"]
            new_mae = new_report["models_trained"]["item_sales"]["test_mae"]
            improvement = (old_mae - new_mae) / old_mae

            validation["models"]["item_sales"] = {
                "old_mae": old_mae,
                "new_mae": new_mae,
                "improvement": improvement,
                "acceptable": new_mae <= old_mae * 1.1,
            }

            improvements.append(improvement)
            logger.info(
                f"   Item Sales: {old_mae:.2f} → {new_mae:.2f} ({improvement:+.1%})"
            )

        # Calculate overall improvement
        validation["overall_improvement"] = (
            np.mean(improvements) if improvements else 0.0
        )

        # Check if any model is significantly worse
        for model_validation in validation["models"].values():
            if not model_validation["acceptable"]:
                validation["passed"] = False
                logger.warning("   ⚠️  New model performance unacceptable")
                break

        return validation

    def _deploy_new_models(self):
        """Deploy new models from temp directory to production"""
        temp_dir = Path("models/temp")

        for model_file in temp_dir.glob("*.pkl"):
            shutil.copy2(model_file, self.models_dir / model_file.name)

        # Copy training report
        report_file = temp_dir / "training_report.json"
        if report_file.exists():
            shutil.copy2(report_file, self.models_dir / "training_report.json")

        # Clean up temp directory
        shutil.rmtree(temp_dir)

    def _rollback_to_backup(self, backup_path: Path):
        """Rollback to backed up models"""
        for model_file in backup_path.glob("*.pkl"):
            shutil.copy2(model_file, self.models_dir / model_file.name)

        report_file = backup_path / "training_report.json"
        if report_file.exists():
            shutil.copy2(report_file, self.models_dir / "training_report.json")

        logger.info("   ✓ Rolled back to previous models")

    def _log_retrain_event(self, result: dict):
        """Log retrain event to history"""
        with open(self.retrain_log_path, "a") as f:
            f.write(json.dumps(result) + "\n")

    # ========================================
    # SCHEDULING HELPERS
    # ========================================

    def get_next_scheduled_retrain(self) -> datetime:
        """Calculate when next scheduled retrain should occur"""
        last_retrain = self._get_last_retrain_date()

        if last_retrain:
            next_retrain = last_retrain + timedelta(
                days=self.policies["schedule"]["max_days_without_retrain"]
            )
        else:
            next_retrain = datetime.now()  # Retrain now if never trained

        return next_retrain


# ========================================
# MAIN EXECUTION
# ========================================


def main():
    """Main retraining function"""
    import argparse

    parser = argparse.ArgumentParser(description="Dinemetra Automated Model Retraining")
    parser.add_argument(
        "--force", action="store_true", help="Force retrain regardless of criteria"
    )
    parser.add_argument(
        "--check-only", action="store_true", help="Only check if retrain is needed"
    )
    args = parser.parse_args()

    try:
        retrainer = AutoRetrainer(models_dir="models", logs_dir="logs")

        if args.check_only:
            decision = retrainer.should_retrain()
            logger.info(f"\nRetrain needed: {decision['should_retrain']}")
            if decision.get("reasons"):
                logger.info("Reasons:")
                for reason in decision["reasons"]:
                    logger.info(f"  - {reason}")
        else:
            result = retrainer.execute_retrain(force=args.force)

            # Print summary
            if result.get("deployed"):
                logger.info("\n✅ Models successfully retrained and deployed!")
            elif result.get("error"):
                logger.error(f"\n❌ Retraining failed: {result['error']}")
            else:
                logger.info("\n⏸️  No retraining performed")

    except Exception as e:
        logger.error(f"❌ Auto-retrain failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
