from typing import TypeVar, Generic

from datatools.jv.model.JValueElement import JValueElement

V = TypeVar('V')


class JPrimitiveElement(Generic[V], JValueElement[V]):
    def __iter__(self):
        yield self
