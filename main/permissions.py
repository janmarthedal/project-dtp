CAN_ADD_DRAFT = 'can_add_draft'
CAN_PUBLISH = 'can_publish'
CAN_ADD_VALIDATION = 'can_add_validation'
CAN_EDIT_KEYWORDS = 'can_edit_keywords'

def has_perm(perm_name, user):
    return user.is_authenticated and user.username == 'jan.marthedal'
