def get_model_fields(model):
    return [f.name for f in model._meta.get_fields()]
