from mongoengine import connect, Document, IntField, StringField, BooleanField

connect('shedule_bot')


class User(Document):
    chat_id = IntField()
    first_name = StringField()
    last_name = StringField()
    username = StringField()
    group = StringField()
    subscribe = BooleanField()

    @staticmethod
    def get_by_chat_id(chat_id):
        try:
            return User.objects.get(chat_id=chat_id)
        except User.DoesNotExist:
            return None
