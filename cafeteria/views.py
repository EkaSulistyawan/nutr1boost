from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from cafeteria.models import Menu
from django.shortcuts import redirect
from django.urls import reverse
from django.templatetags.static import static
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import user_passes_test, login_required
from django.db.models import F, Value, Func
from django.db.models.functions import Replace, Lower

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from .langchain_wrapper import LLM_Service
from .object_detection_wrapper import object_detection
from .ocr_wrapper import ocr
from .ocr_tamura_wrapper import GoogleOCR
from time import sleep
from PIL import Image
import pandas as pd
import Levenshtein
import os
import uuid

import json

# init model
llm_model = LLM_Service()
obj_detect_model = object_detection(imsz=512,odd_ths=4)
easyocr_model = ocr()
googleocr_model = GoogleOCR()

# Create your views here.
def user(request):
    menus = list(Menu.objects.all().values())
    template = loader.get_template('master.html')

    for menu in menus:
        menu['img_url'] = static(f'assets/img/{menu["img_name"]}')
        menu['recommended'] = False

    try:
        response = request.session['response']
    except:
        response = ''
    
    # for menu in menus:
    #     if menu['meal_name'].lower() in response['list_meals']:
    #         menu['recommended'] = True
    recommendation_empty = True
    for menu in menus:
        try:
            # Check if the meal name matches an item in the list
            idx = response['list_meals'].index(menu['meal_name'].lower())
            menu['recommended'] = True
            menu['reason'] = response['recommended_meal_detail']  # Store the index of the matching meal
            recommendation_empty = False

        except:
            # If the meal is not in the list, don't change 'recommended' or 'match_index'
            menu['recommended'] = False
            menu['reason'] = ''
    
    # sort menus based on menu['recommended']
    # menus.sort(key=lambda x: x['recommended'], reverse=True)

    context = {
        'menulist':menus,
        'response':response,
        'recommendation_empty':recommendation_empty
    }

    print(response)

    return HttpResponse(template.render(context,request))

def detail(request):
    menus = list(Menu.objects.all().values())
    template = loader.get_template('detail.html')
    detail_responses = []
    detail=request.session['response']['detail_nutritions']
    minimum_intake=request.session['response']['min_nutritions']
    unit=['kcal','gr','gr','gr','gr','mg','gr']
    nutrients=['energy','protein','fat','carbohydrate','fiber','calcium','veggies']
    for i in range(len(nutrients)):
        detail_responses.append(
            {
                'nutrient':nutrients[i],
                'minimum_intake':minimum_intake[i],
                'unit':unit[i],
                'response':detail[i]
            }
        )
    context = {
        'detail_responses':detail_responses,
    }
    return HttpResponse(template.render(context,request))

@csrf_exempt
def recommend(request):
    print("Request: ",request)
    query = request.POST['query']  # Get the search query (defaults to an empty string)
    model = LLM_Service()
    response = model.predict(query)
    request.session['response'] = response # parse this 
    
    return JsonResponse({'redirect_url': reverse('user')})

@csrf_exempt
def request_current_menu_API(request):
    menus = pd.DataFrame(Menu.objects.filter(showmeal=True).values())
    
    if not menus.empty:
        result = []
        menus['variant'] = menus['meal_name'].str.extract(r"\((small|middle|large)\)", expand=True)
        menus['variant'].fillna("single", inplace=True)
        menus['meal_name'] = menus['meal_name'].str.replace(r"\s*\((small|middle|large)\)", "", regex=True)
        menus['food_group'] = menus['meal_name'].factorize()[0] + 1
        # Group by `meal_name` to create the desired JSON structure
        
        for meal_name, group in menus.groupby("meal_name"):
            food_item = {
                "foodId": int(group["food_group"].iloc[0]),  # Get food_group (foodId)
                "name": meal_name,
                "url": f"/static/assets/img/{group['img_name'].iloc[0]}",  # Generate image URL
                "variants": []
            }
            
            # Add variants for the meal
            for _, row in group.iterrows():
                variant = {
                    "variantName": row["variant"].capitalize(),
                    "variantId": int(row["id"]),
                    "price": row["price"],
                    "calories": row["energy"],
                    "protein": row["protein"],
                    "fat": row["fat"],
                    "carbohydrates": row["carbohydrate"]
                }
                food_item["variants"].append(variant)
            
            result.append(food_item)

        # Construct the final JSON format
        final_json = [{
            "category": "Meals",  # You can modify the category if necessary
            "items": result
        }]
    else:
        final_json = []
    print(final_json)
    return JsonResponse(final_json,safe=False)

def parse_recommendation(request,history=[]):
    query = request.POST['query']  # Get the search query (defaults to an empty string)
    response = llm_model.predict(query,history) # parse this

    # create structure the same as response['list_meals']
    
    menus = pd.DataFrame(Menu.objects.annotate(
        meal_name_lower=Lower('meal_name')
        ).filter(
            meal_name_lower__in=[meal.lower() for meal in response['list_meals']]
        ).values())
    
    if not menus.empty:
        result = []
        menus['variant'] = menus['meal_name'].str.extract(r"\((small|middle|large)\)", expand=True)
        menus['variant'].fillna("single", inplace=True)
        menus['meal_name'] = menus['meal_name'].str.replace(r"\s*\((small|middle|large)\)", "", regex=True)
        menus['food_group'] = menus['meal_name'].factorize()[0] + 1
        # Group by `meal_name` to create the desired JSON structure
        
        for meal_name, group in menus.groupby("meal_name"):
            food_item = {
                "foodId": int(group["food_group"].iloc[0]),  # Get food_group (foodId)
                "name": meal_name,
                "url": f"/static/assets/img/{group['img_name'].iloc[0]}",  # Generate image URL
                "variants": []
            }
            
            # Add variants for the meal
            for _, row in group.iterrows():
                variant = {
                    "variantName": row["variant"].capitalize(),
                    "variantId": int(row["id"]),
                    "price": row["price"],
                    "calories": row["energy"],
                    "protein": row["protein"],
                    "fat": row["fat"],
                    "carbohydrates": row["carbohydrate"]
                }
                food_item["variants"].append(variant)
            
            result.append(food_item)

        # Construct the final JSON format
        final_json = [{
            "category": "Meals",  # You can modify the category if necessary
            "items": result
        }]
    else:
        final_json = []

    response['recommended_meals'] = final_json
    response['id'] = str(uuid.uuid4())
    return response

@csrf_exempt
def request_recommendation_API(request):
    request.session['recommendation_response'] = []
    response = parse_recommendation(request)
    del response['notes_history']
    request.session['recommendation_response'].append(response)
    return JsonResponse(request.session['recommendation_response'],safe=False)

@csrf_exempt
def get_new_recommendation_API(request):
    request.session['recommendation_response'][-1]['rating'] = request.POST['rating']
    response = parse_recommendation(request,request.session['recommendation_response'])
    del response['notes_history']
    request.session['recommendation_response'].append(response)
    return JsonResponse(request.session['recommendation_response'],safe=False)

@csrf_exempt
def reset_current_menu_API(request):
    Menu.objects.update(showmeal=False)
    return JsonResponse({'response':'succeed resetting the menu.'})


@csrf_exempt
def detect_current_menu_API(request):
    
    im = request.FILES['image_upload']
    im = Image.open(im)
    method = request.POST.get('method', 'All')

    Menu.objects.update(showmeal=False)

    if method == 'EfficientNet':
        response = obj_detect_model.predict(im)
        # filter those data that is inside 
        # append .png to the end of response keys
        matching_key = [f"{xx}.png" for xx in response.keys()]
        Menu.objects.filter(img_name__in=matching_key).update(showmeal=True)

    elif method == 'EasyOCR':
        response = easyocr_model.predict(im)
        matching_key = [xx for xx in response.keys()]
        database_key = [xx for xx in pd.DataFrame(Menu.objects.all().values())['ja_meal_name'].tolist()]
        # get except the last 
        matches = [
            db_key for db_key in database_key
            if any(Levenshtein.distance(db_key.replace('（大）', '').replace('（小）', '').replace('（中）', ''), key) <= 2 for key in matching_key)
        ]
        Menu.objects.filter(ja_meal_name__in=matches).update(showmeal=True)
    elif method == 'GoogleOCR':
        response = googleocr_model.predict(im)
        print(response)
        matching_key = [xx for xx in response.keys()]
        database_key = [xx for xx in pd.DataFrame(Menu.objects.all().values())['ja_meal_name'].tolist()]
        # get except the last 
        matches = [
            db_key for db_key in database_key
            if any(Levenshtein.distance(db_key.replace('（大）', '').replace('（小）', '').replace('（中）', ''), key) <= 2 for key in matching_key)
        ]
        Menu.objects.filter(ja_meal_name__in=matches).update(showmeal=True)


    return JsonResponse({'response':response})


################################################### chang emenu for admin
@user_passes_test(lambda user:user.is_superuser)
@login_required
def change_menu(request):
    menus = list(Menu.objects.all().values())
    template = loader.get_template('admin/modify_menu.html')
    for menu in menus:
        menu['img_url'] = static(f'assets/img/{menu["img_name"]}')
        menu['recommended'] = False
    context = {
        'menulist':menus,
    }


    return HttpResponse(template.render(context,request))


@user_passes_test(lambda user:user.is_superuser)
@login_required
def register_current_menu(request):
    # Example of accessing specific form data
    selected_meals = [int(x) for x in request.POST.getlist('selected_meals')] # If using a POST form

    menus = list(Menu.objects.all().values())
    # change 'showmeal' field of the menu to true if the id listed in selected_meals and save it

    Menu.objects.filter(id__in=selected_meals).update(showmeal=True)

    # Optionally, reset showmeal to False for meals not in the selected list
    Menu.objects.exclude(id__in=selected_meals).update(showmeal=False)

    # Return a JsonResponse
    return JsonResponse({
        'status': 'changed successfully',
        'selected_meals': selected_meals
    })