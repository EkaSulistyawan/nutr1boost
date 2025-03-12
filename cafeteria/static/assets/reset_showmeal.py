"""
    Run this script under 
    python manage.py shell
"""

import csv
from cafeteria.models import Menu

Menu.objects.all().update(showmeal=False)
print('Success!')