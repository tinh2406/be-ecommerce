class DBRouter:
    """
    A router to control all database operations on models in the
    secondary application.
    """
    def db_for_read(self, model, **hints):
        """
        Attempts to read secondary models go to secondary.
        """
        if model._meta.app_label == 'crawlers':
            return 'mongo'
        return 'default'

    def db_for_write(self, model, **hints):
        """
        Attempts to write secondary models go to secondary.
        """
        if model._meta.app_label == 'crawlers':
            return 'mongo'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the secondary app is involved.
        """
        if obj1._meta.app_label == 'crawlers' or \
           obj2._meta.app_label == 'crawlers':
           return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the secondary app only appears in the 'secondary'
        database.
        """
        if app_label == 'crawlers':
            return db == 'mongo'
        return None