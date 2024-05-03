def pre_mutation(context):
    if context.filename.endswith('models.py'):
        context.skip = True
