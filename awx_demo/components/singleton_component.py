class SingletonComponent(object):

    def __new__(cls, *args, **kargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super(SingletonComponent, cls).__new__(cls)
        return cls._instance
