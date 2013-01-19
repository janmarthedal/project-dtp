def get_user_info(user):
    name = user.get_full_name()
    if not name:
        name = user.username
    return { 'id': user.id, 'name': name }

