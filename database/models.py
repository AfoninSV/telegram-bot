from datetime import datetime

import peewee as pw


db_user = pw.SqliteDatabase("user.db")
db_history = pw.SqliteDatabase("history.db")
db_meal = pw.SqliteDatabase("meal.db")
db_states = pw.SqliteDatabase("states.db")
db_fridge = pw.SqliteDatabase("fridge.db")
db_favorites = pw.SqliteDatabase("favorites.db")


class BaseModel(pw.Model):
    id_key = pw.AutoField()


class User(BaseModel):
    """Stores user data"""

    user_id = pw.TextField()

    class Meta:
        database = db_user


class Meal(BaseModel):
    """
    Stores meal ID, Name, Ingredients quantity
    to cache data and decrease API usage and response time
    """

    meal_id = pw.TextField()
    title = pw.TextField()
    ingredients = pw.TextField()
    ingredients_qty = pw.IntegerField(null=True)

    class Meta:
        database = db_meal


class Favorites(BaseModel):
    """
    Stores user - meal relations as favorites
    """

    user = pw.ForeignKeyField(User, backref="favorites")
    meal = pw.ForeignKeyField(Meal, backref="favorites")

    class Meta:
        database = db_favorites


class States(BaseModel):
    """
    Stores states of users
    """

    user_id = pw.IntegerField()
    state = pw.IntegerField()

    class Meta:
        database = db_states


class History(BaseModel):
    """Stores user commands call history"""

    user_id = pw.IntegerField()
    message = pw.TextField()

    class Meta:
        database = db_history


class Fridge(BaseModel):
    """
    Stores ingredients of user's fridge
    """

    user_id = pw.IntegerField()
    ingredients = pw.TextField()

    class Meta:
        database = db_fridge
