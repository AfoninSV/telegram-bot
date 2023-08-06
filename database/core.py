from typing import Type, Union, Optional, Dict, Any

from peewee import DoesNotExist

from .models import (
    db_history,
    db_meal,
    db_fridge,
    db_favorites,
    History,
    Meal,
    Fridge,
    Favorites,
)


db_history.connect()
db_history.create_tables([History])

db_meal.connect()
db_meal.create_tables([Meal])

db_fridge.connect()
db_fridge.create_tables([Fridge])

db_favorites.connect()
db_favorites.create_tables([Favorites])


def is_exist(func_to_validate):
    """Validates if value exists in database"""

    def wrapped_func(*args, **kwargs):
        try:
            result = func_to_validate(*args, **kwargs)
        except DoesNotExist:
            return False

        return result

    return wrapped_func


class DBInterface:
    """CRUD interface for databases"""

    def __init__(
        self,
        db_instance: Union[db_history, db_meal],
        db_model: Type[History] | Type[Meal],
    ):
        self._db = db_instance
        self._model = db_model

    def insert(self, **kwargs) -> None:
        with self._db.atomic():
            self._model.create(**kwargs)

    @is_exist
    def update(self, column_name: str, value: Any,
               where_field_name: str, where_field_value: Any) -> None:

        with self._db.atomic():
            query = self._model.update({column_name: value}).where(
                getattr(self._model, where_field_name) == where_field_value
            )
            query.execute()

    def read_all(self):
        with self._db.atomic():
            values = self._model.select()
        return values

    @is_exist
    def read_by(self, field_name: str, field_value: str) -> Optional[Dict]:
        with self._db.atomic():
            record = self._model.get(**{field_name: field_value})
            return record.__data__

    @is_exist
    def delete(self, record_id: int) -> bool:
        with self._db.atomic():
            record = self._model.get_by_id(str(record_id))
            record.delete_instance()
            return True


history_interface = DBInterface(db_history, History)
meal_interface = DBInterface(db_meal, Meal)
fridge_interface = DBInterface(db_fridge, Fridge)
favorites_interface = DBInterface(db_favorites, Favorites)
