from django.db import models

class Food(models.Model):
    class Category(models.IntegerChoices):
        RICE = 1, "RICE"
        SOUP = 2, "SOUP"
        MAIN_DISH = 3, "MAIN_DISH"
        SIDE_DISH = 4, "SIDE_DISH"
        DESSERT = 5, "DESSERT"
    
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, null=True)
    calorie = models.FloatField(null=True)
    category = models.IntegerField(choices=Category.choices, null=True)
    nutrition = models.CharField(max_length=255, null=True)
    allergy = models.CharField(max_length=255, null=True)
    
    def __str__(self):
        return self.name or "Unnamed Food"
        
    class Meta:
        db_table = 'food'


class Menu(models.Model):
    class MealType(models.IntegerChoices):
        BREAKFAST = 1, 'Breakfast'
        LUNCH = 2, 'Lunch'
        DINNER = 3, 'Dinner'
    
    id = models.BigAutoField(primary_key=True)
    date = models.DateField(null=True)
    meal_type = models.IntegerField(choices=MealType.choices, null=True)
    evaluation = models.CharField(max_length=255, null=True)
    
    def __str__(self):
        meal_name = self.get_meal_type_display() if self.meal_type else "Unknown Meal"
        date_str = self.date.strftime('%Y-%m-%d') if self.date else "No Date"
        return f"{meal_name} on {date_str}"
        
    class Meta:
        db_table = 'menu'


class FoodMenu(models.Model):
    id = models.BigAutoField(primary_key=True)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, null=True, related_name='food_items', db_column='menu_id')
    food = models.ForeignKey(Food, on_delete=models.CASCADE, null=True, related_name='menu_appearances', db_column='food_id')
    
    def __str__(self):
        menu_str = str(self.menu) if self.menu else "Unknown Menu"
        food_str = str(self.food) if self.food else "Unknown Food"
        return f"{food_str} in {menu_str}"
        
    class Meta:
        db_table = 'food_menu'


class FeedBack(models.Model):
    id = models.BigAutoField(primary_key=True)
    food_menu = models.ForeignKey(FoodMenu, on_delete=models.CASCADE, null=True, related_name='feedbacks', db_column='food_menu_id')
    score = models.FloatField(null=True)
    evaluation = models.CharField(max_length=255, null=True)
    created_at = models.DateField(null=True)
    
    def __str__(self):
        food_menu_str = str(self.food_menu) if self.food_menu else "Unknown Food Menu"
        return f"Feedback for {food_menu_str}: {self.score}"
        
    class Meta:
        db_table = 'feed_back'