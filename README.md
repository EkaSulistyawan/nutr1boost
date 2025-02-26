
# API Specification
# >>>>> Retrieve current menu

This API will give you the current meals served by the cafeteria. Admin must change the `showmeal` for every current meals served.

**Method**: `GET`

**URL**:`/request_current_menu_API/`

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


# >>>>> Do recommendation
This API will provide recommendation.

**Method**: `POST`

**URL**:`request_recommendation_API`

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