from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^home/', views.home),
    url(r'^volunteer/', views.volunteer),
    url(r'^child-information/', views.child_information),
    url(r'^add/', views.add_child),
    url(r'^child/letter/', views.letter),
    url(r'^login/', views.login),
    url(r'^profile/', views.profile),
    url(r'^child/request/', views.send_request),
    url(r'^donor/purchase/', views.purchase),
    url(r'^admin/activities/', views.activities, name='admin_activities'),
    url(r'^admin/approval/', views.approval, name='admin_approvals'),
    url(r'^admin/purchase/', views.admin_purchases, name='admin_purchases'),
    url(r'^admin/children/', views.admin_children, name='admin_children'),
]
