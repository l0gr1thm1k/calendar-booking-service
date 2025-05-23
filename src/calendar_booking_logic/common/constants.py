from pathlib import Path
import pytz

DATA_DIR = str(Path(__file__).parent.parent /'data')
PDT = pytz.timezone("US/Pacific")
