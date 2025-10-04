from __future__ import annotations
from PySide6.QtCore import QObject
from typing import Generic, TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any


ClassInstance = TypeVar("ClassInstance")
QtMeta = type(QObject)

class QSingleton(QtMeta, Generic[ClassInstance]):#type: ignore[valid-type, misc] #Mypy doesn't support dynamic base classes
    """
    A metaclass for creating singleton classes.
    Attribute `singleton_message` can be used to set a message 
    that will be displayed when trying to create multiple instances of the class.
    """

    __instances: dict[str, ClassInstance] = {}
    singleton_message: str|None = None

    def __call__(cls, *args:Any, **kwargs:Any) -> ClassInstance:
        if cls.__name__ in cls.__instances:
            if cls.singleton_message:
                raise RuntimeError(cls.singleton_message)
            
            raise RuntimeError(f"Cannot create multiple instances of class {cls.__name__}. It's singleton.")

        instance:ClassInstance = super().__call__(*args, **kwargs)
        cls.__instances[cls.__name__] = instance
        return instance


