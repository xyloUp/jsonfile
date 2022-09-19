from json import load, loads, dumps
from os.path import exists
from typing import Optional, Any, Iterator
from .exceptions import NotJSONException, InvalidFormatException


class JSONObject:
    """
    Represents A JSON File
    """

    def __init__(self, loaded: Iterator) -> None:
        if not hasattr(loaded, "__iter__"):
            raise TypeError("Item Must Be Iterable")
            
        self.__loaded = loaded

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.__loaded})"
    
    def __str__(self) -> str:
        return f"{self.__loaded}"
    
    def __iter__(self):
        return iter(self.__loaded) if isinstance(self.__loaded, list) else iter(self.__loaded.items())
    
    def __len__(self) -> int:
        return len(self.__loaded)
    
    def __eq__(self, other) -> bool:
        return self.json == (other.json if hasattr(other, "json") else other)
    
    def __getitem__(self, index: str | int):
        try:
            return self.__loaded[index]
        except KeyError:
            raise
        
    def as_string(self, indent=0) -> str:
        """
        returns(string): The JSON Object As A String
        """
        return dumps(self.__loaded, indent=indent)
    
    def dump(self, fp: str, *, file_mode: Optional[str] = "w", indent: Optional[int] = 4):
        """
        Dumps The JSON Object In A File
        params:
            fp(str | Path): File Path To Dump The JSON In
            kwargs (all optional):
                file_mode(Optional[str]): What Mode To Open The File In. Defaults To w
                indent(Optional[int]): How Indented The JSON Will Be. Defaults To 4
        """
        with open(fp, file_mode) as f:
            f.write(self.as_string(indent))
    
    @property
    def json(self):
        """
        returns(collection): A Copy Of The JSON As A Python Object
        """
        return self.__loaded.copy() if hasattr(self.__loaded, "copy") else self.__loaded

    @property
    def obj_type(self):
        """
        returns(class): The Type Of The JSON (eg dict, list etc)
        """
        return type(self.__loaded)

    @classmethod
    def __get_dict(cls, obj):
        """
        Gets The First Dictionary In A JSON Object (recursively)
        params: 
            obj: JSON Object To Check
        """
        if isinstance(obj, list):
            if isinstance(obj[0], dict):
                _ = {}

                for _dict in obj:
                    if isinstance(_dict, dict):
                        _.update(_dict)

                return _
            return cls._JSONObject__get_dict(obj[0])

        raise InvalidFormatException("Unable To Find Dictionary")

    @property
    def as_object(self):
        """
        returns(class):
            The JSON As A Python Object By Creating A Class And Giving It All The Attributes The JSON Object Has
        exceptions:
            InvalidFormatException: No Dictionary Found In JSON Object
        """
        _as_dict = self.as_dict
        _as_dict.update({"as_string": lambda: f"{self.as_dict}"})
        return type("MyJSONOBJ", (), _as_dict)

    @property
    def as_dict(self) -> dict[Any, Any]:
        """
        returns(dict | none): 
            The JSON Object As A Dictionary / The First Dictionary Found In The JSON
        exceptions:
            InvalidFormatException: No Dictionary Found In JSON Object
        """
        try:
            _as_dict = dict(self.__loaded)
        except (TypeError, ValueError):
            _as_dict = self.__get_dict(self.__loaded)
        return _as_dict

    @property
    def as_list(self) -> list[Any]:
        """
        returns(list) A Copy Of The JSON Object As A List
        """
        return [*self.__loaded] if isinstance(self.__loaded, list) else [self.__loaded]

    @classmethod
    def from_file(cls, fp: str, encoding: Optional[str] = None):
        """
        Creates A Instance Of JSONObject From A File Path
        returns: JSONObject
        params:
            fp(str | Path): File Path To The JSON File To Load
            encoding(Optional[str]): Encoding To Open The File With
        exceptions:
            FileNotFoundError: Raised When The File Doesn't Exist
            NotJSONException: Raised When It Is Not A .json File
        """
        if not exists(fp):
            raise FileNotFoundError(f"{fp} Doesn't Exist.")

        if not str(fp).endswith(".json"):
            raise NotJSONException("Not A JSON File")

        with open(fp, "r") if encoding is None else open(fp, "r", encoding=encoding) as f:
            __loaded = load(f)

        return JSONObject(__loaded)


class _DynamicMeta(type):
    """
    Used To Create Classes With Custom Inheritance.
    For Example If You Pass A List Or JSONObject[list] As json_obj The Class Will Inherit List Same With A Dict/Tuple
    exceptions:
        InvalidFormatException: When The Param json_obj Isn't JSON Format
    """

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        """
        Used To Pass Kwargs To _DynamicMeta.__new__
        """
        return super().__prepare__(name, bases, **kwargs)

    def __new__(cls, *args, **kwargs) -> type:
        name, bases, attrs = args
        json_obj = kwargs["json_obj"]
        if not isinstance(json_obj, (list, tuple, dict, JSONObject)):
            raise InvalidFormatException("Invalid Format Provided")
        return type.__new__(cls, "MyDynamicJSONObject",
                            (type(json_obj) if not isinstance(json_obj,
                             JSONObject) else json_obj.obj_type,),
                            attrs)

class DynamicJSONObject:
    """
    Used To Create Classes With Dynamic/Custom Inheritance.
    For Example If You Pass A List Or JSONObject[list] As json_obj The Class Will Inherit List Same With A Dict/Tuple
    DyanmicJSONObject.__new__ Returns An Instance Of The Class With Said Custom Inheritance
    """
    def __new__(cls, json_obj: JSONObject):
        class MDM(metaclass=_DynamicMeta, json_obj=json_obj):
            def __init__(self, *args, **kwargs):
                args = args[0]
                super().__init__(args.json if isinstance(args, JSONObject) else args)
            
            @property
            def as_json_object(self):
                return JSONObject(self.__class__.__mro__[1](self)) # converts DynamicJSONObject To Its Parent (eg list/dict) and then returns it as a JSONObject
                
        return MDM(json_obj)

__all__ = ["JSONObject", "DynamicJSONObject"]