from typing import Dict, Any
import pickle
from redis import Redis
from sqlalchemy.orm import class_mapper, RelationshipProperty


class CacheManager:
    def __init__(
        self,
        redis: Redis,
        prefix: str = "cache",
        model_version: str = "1",
    ) -> None:
        self._redis = redis
        self._prefix = prefix
        self._model_version = model_version

    def _get_version(self, obj_id: str) -> int:
        version_key = f'{self._prefix}_version_{obj_id}'
        version = self._redis.get(version_key)
        if version is None:
            self._redis.set(version_key, 1)
            return 1

        return int(version)

    def _get_cache_key(self, obj_id, version):
        return f'{self._prefix}_{obj_id}_v{version}_model_v{self._model_version}'

    def _serialize(self, obj):
        if obj is None:
            return None

        obj_dict = obj.__dict__.copy()

        obj_dict = {key: value for key, value in obj.__dict__.items() if not key.startswith('_')}

        mapper = class_mapper(obj.__class__)
        for prop in mapper.iterate_properties:
            if isinstance(prop, RelationshipProperty):
                related_obj = getattr(obj, prop.key)
                obj_dict[prop.key] = self._serialize(related_obj)

        return pickle.dumps(obj_dict)

    def _deserialize(self, serialized_obj, model_class) -> Dict:
        obj_dict = pickle.loads(serialized_obj)

        mapper = class_mapper(model_class)
        for prop in mapper.iterate_properties:
            if isinstance(prop, RelationshipProperty):
                if prop.key in obj_dict:
                    related_model_class = prop.mapper.class_
                    obj_dict[prop.key] = self._deserialize(obj_dict[prop.key], related_model_class)

        return model_class(**obj_dict)

    def set(self, obj_id, obj, ttl=3600):
        version = self._get_version(obj_id)
        cache_key = self._get_cache_key(obj_id, version)
        serialized_obj = self._serialize(obj)
        self._redis.set(cache_key, serialized_obj, ex=ttl)

    def get(self, obj_id, model_class) -> Any:
        version = self._get_version(obj_id)
        cache_key = self._get_cache_key(obj_id, version)
        serialized_obj = self._redis.get(cache_key)

        if serialized_obj:
            return self._deserialize(serialized_obj, model_class)

        return None
