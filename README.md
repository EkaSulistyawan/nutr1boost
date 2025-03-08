
# Table of Contents
- [Table of Contents](#table-of-contents)
- [List of URLs](#list-of-urls)
- [API Specification](#api-specification)
  - [\>\>\>\>\> Retrieve current menu](#-retrieve-current-menu)
  - [\>\>\>\>\> Do recommendation](#-do-recommendation)
  - [\>\>\>\>\> Parse menu](#-parse-menu)
- [Docker Preparation](#docker-preparation)

# List of URLs
|URL|Description|Output|
|---|-----------|----------|
|`index`|Base page, normally just go to site. It shows the front page for user where you can see the current menu and do `recommend`|URL `index`|
|`recommend`|URL to recommend the menu upon clicking button. Recommendation is set under `session[response]`|URL `index`|
|`detail`|URL to show detail of reasons behind the recommendation|URL `detail`|
|`request_current_menu_API`|API to request current menu. [Detail](#-retrieve-current-menu)|JSON|
|`request_recommendation_API`|API to do recommendation. [Detail](#-do-recommendation)|JSON|
|`officer/change_menu`|URL for admin to change current menu|URL `officer/register_current_menu`|
|`officer/register_current_menu`|URL that assign current menu, i.e., set `showmeal` of the selected meals to `True` in the database|`None`|

# API Specification
## >>>>> Retrieve current menu

This API will give you the current meals served by the cafeteria. Admin must change the `showmeal` for every current meals served.

**Method**: `GET`

**URL**:`request_current_menu_API/`

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


## >>>>> Do recommendation
This API will provide recommendation.

**Method**: `POST`

**URL**:`request_recommendation_API/`

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
|`verbose_in_function`|boolean|Back-end's interface to output log on the terminal.|

**Example Response (POSTMAN output)**
```
{
    "response": {
        "additional_notes": "24 years old, 50 kg, 165 cm, lactose intolerant.",
        "detail_nutritions": [
            "The minimum energy intake for a 24-year-old female, 50 kg, and 165 cm, should be around 1600 kcal, according to the Mifflin-St Jeor equation, but may vary based on activity levels and individual metabolism (Mifflin et al., 1990).",
            "The recommended daily protein intake for adults is 0.8 grams per kilogram of body weight (Phillips et al., 2016).",
            "Based on the user's weight (50 kg), a minimum fat intake of 0.8 grams per kilogram of body weight is recommended to support hormone production and nutrient absorption ( керемет, 2023).",
            "Based on a study of dietary guidelines (Anderson et al., 2017), the minimum carbohydrate intake should be 130g per day to supply the brain with adequate glucose.",
            "Based on dietary guidelines and considering the user's age, the recommended minimum daily fiber intake is approximately 25 grams (Anderson et al., 2020).",
            "Based on retrieve_papers, a 24-year-old lactose intolerant individual should aim for at least 1000 mg of calcium daily to maintain bone health, according to research (Strauss et al., 2017).",
            "Based on the Dietary Guidelines for Americans, a 24-year-old female with a weight of 50 kg and height of 165 cm should aim for a minimum of 400 grams of vegetables per day (U.S. Department of Agriculture and U.S. Department of Health and Human Services, 2020)."
        ],
        "min_nutritions": [
            1600,
            40,
            40,
            130,
            25,
            1000,
            400
        ],
        "recommended_meal_detail": "Absolutely! Here's a meal plan designed to meet your needs while keeping your lactose intolerance in mind:\n\n**Meal suggestion:**\n\n1.  **Salmon Bowl:** (Appealing dish) A vibrant bowl packed with flavor and healthy fats from salmon.\n    *   *Nutrition facts:* Provides 555 kcal of energy, 18.4g protein, 7.1g fat, 97.9g carbohydrate, and 2.6g fiber, and 4mg calcium.\n    *   *How it meets your needs:* While slightly exceeding your energy and carbohydrate targets, the high protein content is great for muscle maintenance and the healthy fats contribute to overall well-being. We will adjust other meals accordingly.\n\nThis combination is a starting point, and we can further refine it based on your preferences and other options in the menu to ensure a perfect nutritional balance.",
        "list_meals": [
            "salmon bowl"
        ],
        "verbose_in_function": true
    }
}
```

**Notes:**
- I haven't implement reasoning for each recommended meal.
- Meal could be combined, so expect `list_of_meals` grows. Sometimes the LLM recommend combinations of meal to satisfy the nutrients, thus one reasons is needed. 


## >>>>> Parse menu
This API will provide recommendation.

**Method**: `POST`

**URL**:`detect_current_menu/`

**Request Body**:
```
'image_upload' : Image file
```
**Response**:
|Field|Value|Description|
|-----|-----|-----------|
|`response`|JSON|Keys are the file stored file name. Can remove the `.png` for generalization. The value is the odd of that particular meal exist on the uploaded picture|


**Example Response (POSTMAN output)**
```
{"response": {"homemade-curry.png": 9.086359024047852, "chicken-cutlet.png": 8.386346817016602, "stewed-liver-with-satsuma-herb-chicken.png": 5.788483619689941, "boiled-spinach-with-sesame-paste.png": 13.255047798156738, "miso-soup.png": 9.482758522033691, "salt-grilled-mackerel.png": 5.884803771972656, "simmered-bamboo-shoots-with-katsuobushi.png": 4.561811447143555, "miso-soup-with-pork-and-vegetables.png": 8.705536842346191, "fried-pork-belly-rice-bowl.png": 8.39055347442627, "hamburger-steak-with-grated-japanese-radish-sauce.png": 6.475904941558838, "bang-bang-chicken-salada.png": 11.591764450073242, "potato-salad.png": 5.213132381439209, "grilled-pork-with-soybean-rice-bowl.png": 5.803318500518799, "vegetarian-curry.png": 4.76001501083374, "rice.png": 9.551331520080566, "mackerel-stewed-with-ginger.png": 5.954055309295654}}
```

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