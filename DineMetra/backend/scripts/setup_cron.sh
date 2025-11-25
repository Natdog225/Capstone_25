#!/bin/bash
# Setup cron jobs for Dinemetra model monitoring and retraining

# Add these lines to your crontab:
# Run monitoring every day at 2 AM
# 0 2 * * * cd /path/to/dinemetra/backend && /path/to/python scripts/monitor_models.py >> logs/monitor.log 2>&1

# Check if retraining is needed every Sunday at 3 AM
# 0 3 * * 0 cd /path/to/dinemetra/backend && /path/to/python scripts/auto_retrain.py >> logs/retrain.log 2>&1

echo "To setup automated monitoring and retraining, add these lines to your crontab:"
echo ""
echo "# Dinemetra Model Monitoring"
echo "0 2 * * * cd $(pwd) && $(which python) scripts/monitor_models.py >> logs/monitor.log 2>&1"
echo ""
echo "# Dinemetra Auto-Retraining (weekly check)"
echo "0 3 * * 0 cd $(pwd) && $(which python) scripts/auto_retrain.py >> logs/retrain.log 2>&1"
echo ""
echo "Run 'crontab -e' to edit your crontab and paste these lines"