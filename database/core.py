from typing import Type, Optional, Dict, Any

from peewee import DoesNotExist, Model

from .models import (
    db,
    db_history,
    User,
    Meal,
    Favorites,
    History,
)

db.connect()
db.create_tables([User, Meal, Favorites])

db_history.connect()
db_history.create_tables([History])


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
        db_instance,
        db_models: list[Type[Model]],
    ):
        self._db = db_instance
        self._models = {str(model).split(":")[1][1:-1]: model for model in db_models}

    def model(self, source_model_name: str):
        return self._models[source_model_name]

    def insert(self, source_model_name: str, **kwargs) -> None:
        with self._db.atomic():
            self._models[source_model_name].create(**kwargs)

    @is_exist
    def update(self, source_model_name: str,
               column_name: str, value: Any,
               where_field_name: str, where_field_value: Any) -> None:

        with self._db.atomic():
            query = self._models[source_model_name].update({column_name: value}).where(
                getattr(self._models[source_model_name], where_field_name) == where_field_value
            )
            query.execute()

    def read_all(self, source_model_name: str):
        with self._db.atomic():
            values = self._models[source_model_name].select()
        return values

    @is_exist
    def read_by(self, source_model_name: str,
                field_name: str, field_value: str, as_dict=True, **kwargs) -> Optional[Dict]:
        # todo change as_dict to False
        with self._db.atomic():
            record = self._models[source_model_name].get(**{field_name: field_value}, **kwargs)

            if as_dict:
                return record.__data__
            return record

    @is_exist
    def read_by_multi(self, source_model_name: str, **kwargs) -> Optional[Dict]:
        with self._db.atomic():
            record = self._models[source_model_name].get(**kwargs)
            return record

    @is_exist
    def delete(self, source_model_name: str,  record_id: int) -> bool:
        with self._db.atomic():
            record = self._models[source_model_name].get_by_id(str(record_id))
            record.delete_instance()
            return True


db_interface = DBInterface(db, [User, Meal, Favorites])
history_interface = DBInterface(db_history, [History])
