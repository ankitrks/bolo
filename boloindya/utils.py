from django.contrib import admin
def admin_all(model):
    for obj in model.__dict__.values():
        try:
            admin.site.register(obj)
        except Exception, e:
            pass