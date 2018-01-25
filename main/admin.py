from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import ugettext_lazy as _

from main.models import UserInfo, User, Child, Volunteer, Donor, Letter, Need, PurchaseForInstitute, PurchaseForNeed, \
    Activity, OngoingUserInfo


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    class UserInfoInline(admin.TabularInline):
        model = UserInfo
        extra = 1
        max_num = 1

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'userinfo', 'is_staff')
    search_fields = ('email', 'userinfo__first_name', 'userinfo__last_name')
    ordering = ('email',)
    inlines = [UserInfoInline]


admin.site.unregister(Group)
admin.site.register(Child)
admin.site.register(Volunteer)
admin.site.register(Donor)
admin.site.register(Letter)
admin.site.register(Need)
admin.site.register(PurchaseForInstitute)
admin.site.register(PurchaseForNeed)
admin.site.register(Activity)
admin.site.register(OngoingUserInfo)
