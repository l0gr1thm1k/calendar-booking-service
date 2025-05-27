import os
from pathlib import Path
import pytz

from dotenv import load_dotenv

load_dotenv()

DATA_DIR = str(Path(__file__).parent.parent / 'data')
SHARED_MOUNT_DIR = str(Path(__file__).parent.parent.parent.parent / 'shared_mount')
PDT = pytz.timezone("US/Pacific")
DEFAULT_AGENT_IDENTIFIER = os.getenv('DEFAULT_AGENT_IDENTIFIER')