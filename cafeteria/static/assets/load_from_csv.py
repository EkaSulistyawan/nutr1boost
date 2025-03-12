"""
    Run this script under 
    python manage.py shell
"""

import csv
from cafeteria.models import Menu

with open('./cafeteria/static/assets/menulist_v4_jaMealName_jaSupport.csv', newline='', encoding='utf-8-sig') as file:
    reader = csv.DictReader(file)
    data = [
        Menu(
            meal_name       = row['meal_name'],
            ja_meal_name    = row['ja_meal_name'],
            meal_type       = row['meal_type'],
            description     = row['description'],
            img_name        = row['img_name'],
            showmeal        = row['showmeal'],
            price           = row['price'],
            energy          = row['energy'],
            protein         = row['protein'],
            fat             = row['fat'],
            carbohydrate    = row['carbohydrate'],
            fiber           = row['fiber'],
            calcium         = row['calcium'],
            veggies         = row['veggies'],
        ) for row in reader
    ]

Menu.objects.bulk_create(data)
print('Success!')