from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^home/', views.home),
    url(r'^volunteer/', views.volunteer, name='volunteer_children'),
    url(r'^child-information/', views.child_information, name='child_information'),
    url(r'^child/add/', views.add_child, name='add_child'),
    url(r'^child/edit/', views.edit_child),
    url(r'^child/letter/', views.letter, name='child_letter'),
    url(r'^login/', views.login, name='login'),
    url(r'^profile/', views.profile, name='profile'),
    url(r'^child/request/', views.send_request, name='child_request'),
    url(r'^donor/purchase/', views.purchase, name='donor_purchase'),
    url(r'^admin/activities/', views.activities, name='admin_activities'),
    url(r'^admin/approval/', views.approval, name='admin_approvals'),
    url(r'^admin/purchase/', views.admin_purchases, name='admin_purchases'),
    url(r'^admin/children/', views.admin_children, name='admin_children'),
]
