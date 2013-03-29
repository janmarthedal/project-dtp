
def init_context(active_nav):
    if active_nav.upper() == 'D':
        active_nav = 'definitions'
    elif active_nav.upper() == 'T':
        active_nav = 'theorems'
    elif active_nav.upper() == 'P':
        active_nav = 'proofs'
    return { 'active_nav': active_nav }
