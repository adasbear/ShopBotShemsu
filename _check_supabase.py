import sys, os
sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv()
from supabase import create_client
import supabase

print(f'supabase-py version: {supabase.__version__ if hasattr(supabase, "__version__") else "unknown"}')
s = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
methods = [m for m in dir(s) if not m.startswith('_')]
print('Client methods:', methods)
