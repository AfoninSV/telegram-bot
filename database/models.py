import peewee as pw


db = pw.SqliteDatabase("database.db")  # for User, Meal, Favorites
db_history = pw.SqliteDatabase("history.db")
db_states = pw.SqliteDatabase("states.db")


class BaseModel(pw.Model):
    id = pw.AutoField()

    class Meta:
        database = db


class User(BaseModel):
    """Stores user data"""

    user_id = pw.TextField()


class Meal(BaseModel):
    """
    Stores meal ID, Name, Ingredients quantity
    to cache data and decrease API usage and response time
    """

    meal_id = pw.TextField()
    title = pw.TextField()
    ingredients = pw.TextField()
    ingredients_qty = pw.IntegerField()


class Favorites(BaseModel):
    """
    Stores user - meal relations as 'favorites'
    """

    user = pw.ForeignKeyField(User, backref="favorites")
    meal = pw.ForeignKeyField(Meal, backref="favorites")


class History:
    """Stores user commands call history"""

    id = pw.AutoField()
    user_id = pw.IntegerField()
    message = pw.TextField()

    class Meta:
        database = db_history
