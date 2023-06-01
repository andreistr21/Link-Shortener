def update_immutable_user_fields(user, *args, **kwargs):
    """Updates immutable fields"""
    user.is_email_confirmed = True
    user.save()

    return {"user": user}
