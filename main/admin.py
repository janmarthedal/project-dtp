from items.models import Item, Tag, ItemTag
from django.contrib import admin

class ItemTagsInline(admin.TabularInline):
    model = ItemTag

class ItemAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'status')
    actions = ['make_final_action', 'make_review_action']
    inlines = [ItemTagsInline]

    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ['modified_by', 'deps', 'final_at', 'final_id', 'status']
        self.readonly_fields = []
        self.radio_fields = {}
        if obj:
            self.readonly_fields.append('parent')
            self.readonly_fields.append('created_by')
            self.readonly_fields.append('kind')
        else:
            self.exclude.append('created_by')
            self.radio_fields['kind'] = admin.HORIZONTAL
        return super(ItemAdmin, self).get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        obj.status = 'D'
        obj.modified_by = request.user
        if not change:
            obj.created_by = request.user
        obj.save()

    def make_final_action(self, request, queryset):
        for item in queryset:
            item.make_final(request.user)
    make_final_action.short_description = 'Make selected items final'

    def make_review_action(self, request, queryset):
        for item in queryset:
            item.make_review(request.user)
    make_review_action.short_description = 'Make selected items under review'

admin.site.register(Item, ItemAdmin)
admin.site.register(Tag)
admin.site.register(ItemTag)

