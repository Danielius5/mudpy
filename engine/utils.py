import typing
import json

def search_subs(subs, name):
    for sub in subs:
        if sub.__name__ == name:
            return sub
        result = search_subs(sub.__subclasses__(), name)
        if result is not None:
            return result
    return None


class DataMapping(typing.MutableMapping):    
    def __getitem__(self, key):
        if key not in self.data:
            raise KeyError(key)
        return self.data[key]

    def __setitem__(self, key, value):
        if key not in self.data:
            raise KeyError(key)
        self.data[key] = value

    def __delitem__(self, key):
        if key not in self.data:
            raise KeyError(key)
        self.data[key] = None

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def __repr__(self):
        return f"<{self.__class__.__name__}={self.data}>"
    
    def to_json(self):
        return json.dumps(self.data)
    
    @classmethod
    def from_json(cls, data):
        data = json.loads(data)
        return cls(**data)
    

