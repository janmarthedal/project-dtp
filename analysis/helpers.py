from math import expm1, atan, pi

def queryset_generator(queryset):
    items = queryset.order_by('pk')[:100]
    while items:
        latest_pk = items[len(items) - 1].pk
        for item in items:
            yield item
        items = queryset.filter(pk__gt=latest_pk).order_by('pk')[:100]

def compute_score(refer_count, max_points):
    max_points = max_points or 0
    importance = 0.01 - 0.99*expm1(-refer_count)
    s = 1000 if max_points > 0 else 2
    p = 2 * (s - 1) / pi * atan(0.5 * max_points * pi / (s - 1)) + 1
    return p / importance
