import mongoengine as me


class Well(me.DynamicDocument):

    # meta = {'ordering': ['-published_date']}

    api14 = me.StringField()


if __name__ == "__main__":
    from ihs.config import get_active_config
    from ihs import create_app, db

    conf = get_active_config()
    app = create_app()
    app.app_context().push()

    well = Well(api14="12345678901234")
    well.save()
