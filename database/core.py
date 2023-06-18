from .models import db_history, db_meal, db_states, History, Meal, States
from typing import Type, Union, Optional, Dict, Any
from peewee import DoesNotExist

db_history.connect()
db_history.create_tables([History])

db_meal.connect()
db_meal.create_tables([Meal])

db_states.connect()
db_states.create_tables([States])


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

    def __init__(self, db_instance: Union[db_history, db_meal],
                 db_model: Type[History] | Type[Meal]):
        self._db = db_instance
        self._model = db_model

    def insert(self, **kwargs) -> None:
        with self._db.atomic():
            self._model.create(**kwargs)

    def update(self, column_name: str, value: Any, **kwargs):
        with self._db.atomic():
            query = self._model.update({column_name: value}).where(self._model.user_id == kwargs['user_id'])
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
states_interface = DBInterface(db_states, States)
