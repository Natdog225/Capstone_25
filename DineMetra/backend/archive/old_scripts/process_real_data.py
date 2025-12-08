"""
Process real restaurant data and prepare for model training
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from etl.extract_real_data import RealDataExtractor
import logging

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    from etl.extract_real_data import main
    main()