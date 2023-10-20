def hasmethod(obj:object,method_name:str):
    return hasattr(obj,method_name) and callable(getattr(obj,method_name))