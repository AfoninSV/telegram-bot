from datetime import datetime
import peewee as pw

db_history = pw.SqliteDatabase("history.db")
db_meal = pw.SqliteDatabase("meal.db")


class BaseModel(pw.Model):
    id_key = pw.AutoField()
    date_time = pw.DateTimeField(default=datetime.now().strftime("%d-%m-%y %H:%M:%S"))


class History(BaseModel):
    """Stores user commands call history"""

    message = pw.TextField()

    class Meta:
        database = db_history


class Meal(BaseModel):
    """
    Stores meal ID, Name, Ingredients quantity
    to cache data and decrease API usage and response time
    """

    meal_id = pw.TextField()
    ingredients = pw.TextField()

    class Meta:
        database = db_meal
