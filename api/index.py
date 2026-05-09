import os
import sys

# Add the root directory to the path so we can import from 'Backend'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the consolidated app from Backend/app.py
from Backend.app import app

# Vercel needs the 'app' object to be available at the module level
# When Vercel imports this file, it will find 'app' here.
