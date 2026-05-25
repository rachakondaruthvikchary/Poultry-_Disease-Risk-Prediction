import os
import sys
from pathlib import Path

# Add function directory to python path
func_dir = Path(__file__).resolve().parent
sys.path.append(str(func_dir))

from mangum import Mangum
from app.main import app

# Create the standard mangum handler
mangum_handler = Mangum(app)

def handler(event, context):
    # Adjust path if needed so FastAPI matches it correctly
    # Netlify passes the request path in event['path'] or event['rawPath']
    prefix = "/.netlify/functions/api"
    
    if 'path' in event:
        if event['path'].startswith(prefix):
            event['path'] = event['path'][len(prefix):]
            
    if 'rawPath' in event:
        if event['rawPath'].startswith(prefix):
            event['rawPath'] = event['rawPath'][len(prefix):]
            
    return mangum_handler(event, context)
