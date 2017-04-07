def has_perm(name, user):
    return user.is_authenticated and name in user.userdata.perms.split(',')
