# Singleton Design Pattern
class Configuration:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Configuration, cls).__new__(cls)
            cls.dataset_path = None
        return cls._instance