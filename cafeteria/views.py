from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from cafeteria.models import Menu
from django.shortcuts import redirect
from django.urls import reverse
from django.templatetags.static import static
from django.contrib import messages
from .langchain_wrapper import LLM_Service
from time import sleep

import json

## for prediction


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

def recommend(request):
    print("Request: ",request)
    query = request.POST['query']  # Get the search query (defaults to an empty string)
    model = LLM_Service()
    response = model.predict(query)
    request.session['response'] = response
    
    return JsonResponse({'redirect_url': reverse('user')})