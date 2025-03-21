
# Table of Contents
- [About](#about)
- [Table of Contents](#table-of-contents)
- [Docker Preparation](#docker-preparation)
- [List of URLs](#list-of-urls)
- [API Specification](#api-specification)
  - [\>\>\>\>\> Retrieve current menu](#retrieve-current-menu)
  - [\>\>\>\>\> Do recommendation](#do-recommendation)
  - [\>\>\>\>\> Get new recommendation](#get-new-recommendation)
  - [\>\>\>\>\> Detect and set current menu](#detect-and-set-current-menu)
  - [\>\>\>\>\> Reset current menu](#reset-current-menu)

# About
No more hassle to eat at the cafeteria! You can make your order, see the menu and ask AI to get the meal for you! Enjoy our CafeterAI :)

This project is a product of BOOST Team 1, thanks for your contributions!
[![Contributors](https://contrib.rocks/image?repo=EkaSulistyawan/nutr1boost)](https://github.com/EkaSulistyawan/nutr1boost/graphs/contributors)

# Docker Preparation

Make sure you install docker and run the service. [Getting started with Docker](https://docs.docker.com/desktop/setup/install/windows-install/)

Step to reproduce docker image (tested on Windows 11)

(1) Clone the repo

(2) Go to directory where `Dockerfile` is stored

(3) Run the following script on command prompt to make the image,
```
docker build -t nutr1boost:1.0 .
```

(4) Run the following script in command prompt to run the image
```
docker run -it -p 127.0.0.1:8000:8000 -e GOOGLE_API_KEY=<your gemini api key> -e TAVILY_API_KEY=<your tavily key> nutr1boost:1.0
```

This step sets up everything you need to run the LLM. If you wish to change any interface of the LLM, you may want to modify the file where the LLM is used. `cafeteria/langchain_wrapper.py`

(5) Open browser and go to `127.0.0.1:8000`

# List of URLs
|URL|Description|Output|
|---|-----------|----------|
|`index`|Base page, normally just go to site. It shows the front page for user where you can see the current menu and do `recommend`|URL `index`|
|`recommend`|URL to recommend the menu upon clicking button. Recommendation is set under `session[response]`|URL `index`|
|`detail`|URL to show detail of reasons behind the recommendation|URL `detail`|
|`api/request_current_menu/`|API to request current menu. [Detail](#retrieve-current-menu)|JSON|
|`api/request_recommendation/`|API to do recommendation. [Detail](#do-recommendation)|JSON|
|`api/get_new_recommendation/`|API to renew recommendation, added additional info `rating`. [Detail](#get-new-recommendation)|JSON|
|`api/detect_and_set_current_menu/`|API to do set the menu based on image. [Detail](#detect-and-set-current-menu)|JSON|
|`api/reset_current_menu/`|API to reset `showmeal`. [Detail](#reset-current-menu)|JSON|
|`officer/change_menu`|URL for admin to change current menu|URL `officer/register_current_menu`|
|`officer/register_current_menu`|URL that assign current menu, i.e., set `showmeal` of the selected meals to `True` in the database|`None`|

# API Specification
## Retrieve current menu

This API will give you the current meals served by the cafeteria. Admin must change the `showmeal` for every current meals served.

**Method**: `GET`

**URL**:`api/request_current_menu/`

**Response**:
|Field|Value|Description|
|-----|-----|-----------|
|`meal_name`|string|name of the meal|
|`meal_type`|string|now it could be `main` for main course, or `alacarte`|
|`description`|string|description of the menu|
|`img_name`|string|the name of the image associated with the menu. Retrieve the image directly from `<URL>/static/assets/img/<img_name>`|
|`showmeal`|boolean|whether the meal is currently served or not|
|`price`|float|price of the menu|
|`energy`|float|calories for specified menu (kcal)|
|`protein`|float|protein for specified menu (gr)|
|`fat`|float|fat for specified menu (gr)|
|`carbohydrate`|float|carbohydrate for specified menu (gr)|
|`fiber`|float|fiber for specified menu (gr)|
|`calcium`|float|calcium for specified menu (mg)|
|`veggies`|float|veggies for specified menu (gr)|

**Example Response (POSTMAN output)**:
```
{
    "menuItems": [
        {
            "id": 76,
            "meal_name": "Salmon Bowl",
            "meal_type": "main",
            "description": "test description",
            "img_name": "salmon-bowl.png",
            "showmeal": true,
            "price": 561,
            "energy": 555.0,
            "protein": 18.4,
            "fat": 7.1,
            "carbohydrate": 97.9,
            "fiber": 2.6,
            "calcium": 4.0,
            "veggies": 0.0
        }
    ]
}
```

**Notes**:
- This approach needs `admin` to modify the menu.


## Do recommendation
This API will provide recommendation.

**Method**: `POST`

**URL**:`api/request_recommendation/`

**Request Body**:
```
'query' : "24 years old, 50 kg, 165 cm, lactose intolerant."
```
**Response**:
|Field|Value|Description|
|-----|-----|-----------|
|`additional_notes`|string|Value of `query` in the request body. It will be passed as additonal notes to the LLM|
|`detail_nutritions`|list of strings, length 7|Detail nutrition inferred for each nutrients. This time, it should have length of 7 for each nutrition|
|`min_nutritions`|list of float|minimum daily intake for each nutrition. This time, it should have length of 7 for each nutrtion|
|`recommended_meal_detail`|string|Reasons behind recommendation. Wrapped for **ALL** meal. |
|`list_meals`|list of string|list of recommended meal name. Name is match with `Retrieve Current Menu`|
|`recommended_meals`|list of JSON|List of recommended meals. Restructured `list_meals` same with `Retrieve Current Menu`|
|`verbose_in_function`|boolean|Back-end's interface to output log on the terminal.|

**Example Response (POSTMAN output)**
```
[
    {
        "additional_notes": "i'm 24 years old, 165 cm tall and 56 kg",
        "detail_nutritions": [
            "Based on retrieve_papers, the estimated minimum energy requirement for a 24-year-old, 165 cm tall, and 56 kg individual is approximately 1600 kcal (FAO, WHO, & UNU, 2004).",
            "The recommended minimum protein intake for adults is 0.8 grams per kilogram of body weight (Phillips et al., 2016).",
            "Based on a search query regarding the minimum fat intake for a young adult with the provided height and weight, a retrieved paper suggests that a minimum of 0.8 grams of fat per kilogram of body weight is necessary for hormonal regulation and nutrient absorption [WARNING] (URL: https://www.eatright.org/]",
            "Based on dietary guidelines and considering the user's age, height, and weight, a minimum carbohydrate intake of 130 grams per day is recommended to support basic metabolic functions (EFSA, 2010).",
            "Based on dietary guidelines, the recommended minimum daily intake of fiber is approximately 25 grams for women [WARNING] (https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/expert-answers/how-many-grams-of-fiber-do-you-need-daily/faq-20058883).",
            "The recommended daily allowance of calcium for adults aged 19-50 is 1000 mg per day (National Institutes of Health, n.d.).",
            "Based on a general recommendation for adults, a minimum of 400 grams of fruits and vegetables per day is suggested for overall health (WHO, 2003)."
        ],
        "min_nutritions": [
            1600,
            45,
            45,
            130,
            25,
            1000,
            400
        ],
        "recommended_meal_detail": "Fuel your body with our delicious and nutritious meal plan! Indulge in the comforting flavors of **Homemade Curry (small)** paired with the delicate **Simmered-Bamboo-Shoots-With katsuobushi**. This combination delivers approximately 552 kcal of energy, 14.7g of protein to support your muscles, 13.7g of fat, and 88.7g of carbohydrates for sustained energy. You'll also benefit from 4.8g of fiber, 35mg of calcium, and 96g of veggies, providing essential nutrients for a healthy and balanced diet. Enjoy!",
        "list_meals": [
            "homemade curry (small)",
            "simmered-bamboo-shoots-with katsuobushi"
        ],
        "verbose_in_function": true,
        "recommended_meals": [
            {
                "category": "Meals",
                "items": [
                    {
                        "foodId": 1,
                        "name": "Homemade Curry",
                        "url": "/static/assets/img/homemade-curry.png",
                        "variants": [
                            {
                                "variantName": "Small",
                                "variantId": 310,
                                "price": 286,
                                "calories": 519.0,
                                "protein": 12.4,
                                "fat": 13.6,
                                "carbohydrates": 83.0
                            }
                        ]
                    },
                    {
                        "foodId": 2,
                        "name": "Simmered-Bamboo-Shoots-With katsuobushi",
                        "url": "/static/assets/img/simmered-bamboo-shoots-with-katsuobushi.png",
                        "variants": [
                            {
                                "variantName": "Single",
                                "variantId": 352,
                                "price": 99,
                                "calories": 33.0,
                                "protein": 2.0,
                                "fat": 0.1,
                                "carbohydrates": 6.0
                            }
                        ]
                    }
                ]
            }
        ],
        "id": "b93b1742-d1e3-4a60-8d73-d5377c0da162"
    }
]
```

**Notes:**
- I haven't implement reasoning for each recommended meal.
- Meal could be combined, so expect `list_of_meals` grows. Sometimes the LLM recommend combinations of meal to satisfy the nutrients, thus one reasons is needed. 

## Get new recommendation
This API append new recommendation to an existing history of recommendation. The history is stored in a session and will be resetted when `api/request_recommendation/` is hitted. It also accepts `rating` of the latest recommendation for the LLM to provide fresh recommendation. **NOTE: PLEASE LIMIT THE NEW RECOMMENDATION UP TO 2 TIMES, since this is still using free Gemini API :\(** 

**Method**: `POST`

**URL**: `api/get_new_recommendation/`

**Request Body**:
```
'query' : "24 years old, 50 kg, 165 cm, lactose intolerant."
'rating': Can be either, "Good", "Neutral", and "Bad". Basically can put any sentence that describes the quality of the previous recommendation.
```

**Response**:
List of structure same with [`api/request_recommendation`](#do-recommendation), with added `id` to track down history of recommendation and `rating` for every recommendation history except the latest recommendation.

**Example Response (POSTMAN output)**:
```
[
    {
        "additional_notes": "i'm 24 years old, 165 cm tall and 56 kg",
        "detail_nutritions": [
            "Based on retrieve_papers, the estimated minimum energy requirement for a 24-year-old, 165 cm tall, and 56 kg individual is approximately 1600 kcal (FAO, WHO, & UNU, 2004).",
            "The recommended minimum protein intake for adults is 0.8 grams per kilogram of body weight (Phillips et al., 2016).",
            "Based on a search query regarding the minimum fat intake for a young adult with the provided height and weight, a retrieved paper suggests that a minimum of 0.8 grams of fat per kilogram of body weight is necessary for hormonal regulation and nutrient absorption [WARNING] (URL: https://www.eatright.org/]",
            "Based on dietary guidelines and considering the user's age, height, and weight, a minimum carbohydrate intake of 130 grams per day is recommended to support basic metabolic functions (EFSA, 2010).",
            "Based on dietary guidelines, the recommended minimum daily intake of fiber is approximately 25 grams for women [WARNING] (https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/expert-answers/how-many-grams-of-fiber-do-you-need-daily/faq-20058883).",
            "The recommended daily allowance of calcium for adults aged 19-50 is 1000 mg per day (National Institutes of Health, n.d.).",
            "Based on a general recommendation for adults, a minimum of 400 grams of fruits and vegetables per day is suggested for overall health (WHO, 2003)."
        ],
        "min_nutritions": [
            1600,
            45,
            45,
            130,
            25,
            1000,
            400
        ],
        "recommended_meal_detail": "Fuel your body with our delicious and nutritious meal plan! Indulge in the comforting flavors of **Homemade Curry (small)** paired with the delicate **Simmered-Bamboo-Shoots-With katsuobushi**. This combination delivers approximately 552 kcal of energy, 14.7g of protein to support your muscles, 13.7g of fat, and 88.7g of carbohydrates for sustained energy. You'll also benefit from 4.8g of fiber, 35mg of calcium, and 96g of veggies, providing essential nutrients for a healthy and balanced diet. Enjoy!",
        "list_meals": [
            "homemade curry (small)",
            "simmered-bamboo-shoots-with katsuobushi"
        ],
        "verbose_in_function": true,
        "recommended_meals": [
            {
                "category": "Meals",
                "items": [
                    {
                        "foodId": 1,
                        "name": "Homemade Curry",
                        "url": "/static/assets/img/homemade-curry.png",
                        "variants": [
                            {
                                "variantName": "Small",
                                "variantId": 310,
                                "price": 286,
                                "calories": 519.0,
                                "protein": 12.4,
                                "fat": 13.6,
                                "carbohydrates": 83.0
                            }
                        ]
                    },
                    {
                        "foodId": 2,
                        "name": "Simmered-Bamboo-Shoots-With katsuobushi",
                        "url": "/static/assets/img/simmered-bamboo-shoots-with-katsuobushi.png",
                        "variants": [
                            {
                                "variantName": "Single",
                                "variantId": 352,
                                "price": 99,
                                "calories": 33.0,
                                "protein": 2.0,
                                "fat": 0.1,
                                "carbohydrates": 6.0
                            }
                        ]
                    }
                ]
            }
        ],
        "id": "b93b1742-d1e3-4a60-8d73-d5377c0da162",
        "rating": "Neutral"
    },
    {
        "additional_notes": "anything other than curry",
        "detail_nutritions": [
            "Based on retrieve_papers, the estimated minimum energy requirement for a 24-year-old, 165 cm tall, and 56 kg individual is approximately 1600 kcal (FAO, WHO, & UNU, 2004).",
            "The recommended minimum protein intake for adults is 0.8 grams per kilogram of body weight (Phillips et al., 2016).",
            "A minimum of 0.8 grams of fat per kilogram of body weight is necessary for hormonal regulation and nutrient absorption (https://www.eatright.org/)",
            "Based on dietary guidelines and considering the user's age, height, and weight, a minimum carbohydrate intake of 130 grams per day is recommended to support basic metabolic functions (EFSA, 2010).",
            "Based on dietary guidelines, the recommended minimum daily intake of fiber is approximately 25 grams for women (https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/expert-answers/how-many-grams-of-fiber-do-you-need-daily/faq-20058883) [WARNING].",
            "The recommended daily allowance of calcium for adults aged 19-50 is 1000 mg per day (National Institutes of Health, n.d.).",
            "Considering previous recommendation of 400 grams of fruits and vegetables per day for overall health (WHO, 2003) and excluding curry, the minimum intake of veggies remains at 400 grams."
        ],
        "min_nutritions": [
            1600,
            45,
            45,
            130,
            25,
            1000,
            400
        ],
        "recommended_meal_detail": "Craving something other than curry? We've got you covered! Indulge in the delightful combination of **Mackerel stewed with ginger** and **Chicken cutlet**! This pairing provides approximately 439 kcal of energy, 22.4g of protein to support your muscles, 28.8g of fat, and 17.8g of carbohydrates for sustained energy. You'll also benefit from 1.2g of fiber and 5mg of calcium. Enjoy this protein-rich and flavorful alternative!",
        "list_meals": [
            "mackerel stewed with ginger",
            "chicken cutlet"
        ],
        "verbose_in_function": true,
        "recommended_meals": [
            {
                "category": "Meals",
                "items": [
                    {
                        "foodId": 2,
                        "name": "Chicken cutlet",
                        "url": "/static/assets/img/chicken-cutlet.png",
                        "variants": [
                            {
                                "variantName": "Single",
                                "variantId": 315,
                                "price": 187,
                                "calories": 231.0,
                                "protein": 12.9,
                                "fat": 14.6,
                                "carbohydrates": 12.2
                            }
                        ]
                    },
                    {
                        "foodId": 1,
                        "name": "Mackerel stewed with ginger",
                        "url": "/static/assets/img/mackerel-stewed-with-ginger.png",
                        "variants": [
                            {
                                "variantName": "Single",
                                "variantId": 313,
                                "price": 242,
                                "calories": 208.0,
                                "protein": 9.5,
                                "fat": 14.2,
                                "carbohydrates": 5.6
                            }
                        ]
                    }
                ]
            }
        ],
        "id": "74ac0ec1-c5aa-4512-a264-e0e670c8a020"
    }
]
```

## Detect and set current menu
This API will use either OCR/EfficientNet

**Method**: `POST`

**URL**: `api/detect_and_set_current_menu/`

**Request Body**:
```
'image_upload' : Image file
'method' : Method used for menu inference. Either `GoogleOCR`, `Easy OCR` or `EfficientNet`
```
**Response**:
|Field|Value|Description|
|-----|-----|-----------|
|`response`|JSON|Keys are the file stored file name. Can remove the `.png` for generalization. The value is the odd of that particular meal exist on the uploaded picture|


**Example Response (POSTMAN output)**
```
{"response": {"homemade-curry.png": 9.086359024047852, "chicken-cutlet.png": 8.386346817016602, "stewed-liver-with-satsuma-herb-chicken.png": 5.788483619689941, "boiled-spinach-with-sesame-paste.png": 13.255047798156738, "miso-soup.png": 9.482758522033691, "salt-grilled-mackerel.png": 5.884803771972656, "simmered-bamboo-shoots-with-katsuobushi.png": 4.561811447143555, "miso-soup-with-pork-and-vegetables.png": 8.705536842346191, "fried-pork-belly-rice-bowl.png": 8.39055347442627, "hamburger-steak-with-grated-japanese-radish-sauce.png": 6.475904941558838, "bang-bang-chicken-salada.png": 11.591764450073242, "potato-salad.png": 5.213132381439209, "grilled-pork-with-soybean-rice-bowl.png": 5.803318500518799, "vegetarian-curry.png": 4.76001501083374, "rice.png": 9.551331520080566, "mackerel-stewed-with-ginger.png": 5.954055309295654}}
```

## Reset current menu
This API sets all `showmeal` field of the database to `false`.

**Method**: `POST`

**URL**: `api/reset_current_menu/`

**Request Body**:
```
None
```

**Response**:
```
only simple JSON showing `succeed resetting the menu.`. But, when you go to the main page, All menu is empty.
```

**Example Response (POSTMAN output)**
```
{
    "response": "succeed resetting the menu."
}
```