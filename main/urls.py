from django.conf.urls import url
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    url(r'^home/', views.home),
    url(r'^volunteer/children$', views.volunteer, name='volunteer_children'),
    url(r'^child-information/(?P<child_id>\d+)/', views.child_information, name='child_information'),
    url(r'^(?P<user_class>\w+)/add/', views.add_user, name='add_user'),
    url(r'^(?P<user_class>\w+)/edit/', views.modify_user, name='edit_user'),
    url(r'^child/letter/', views.letter, name='child_letter'),
    url(r'^child/request/', views.send_request, name='child_request'),
    url(r'^child/change-volunteer/', views.change_volunteer, name='change_volunteer'),
    url(r'^child/purchases/', views.child_purchases, name='child_purchases'),
    url(r'^login/', views.login, name='login'),
    url(r'^profile/', views.profile, name='profile'),
    url(r'^volunteer/letter-verification/', views.volunteer_letter_verification, name='volunteer_letter_verification'),
    url(r'^donor/purchase/', views.purchase, name='donor_purchase'),
    url(r'^donor/purchases/', views.donor_purchases, name='donor_purchases'),
    url(r'^admin/activities/', views.activities, name='admin_activities'),
    url(r'^admin/approval/', views.approval, name='admin_approvals'),
    url(r'^admin/purchases/', views.admin_purchases, name='admin_purchases'),
    url(r'^admin/children/', views.admin_children, name='admin_children'),
    url(r'^donor/sponsored-children/', views.sponsored_children, name='sponsored_children'),
    url(r'^admin/unresolveds/', views.admin_unresolveds, name='admin_unresolveds'),
    url(r'^admin/volunteers/', views.admin_volunteers, name='admin_volunteers'),
    url(r'^history/', TemplateView.as_view(template_name='main/static/history.html'), name='static_history'),
    url(r'^vision/', TemplateView.as_view(template_name='main/static/vision.html'), name='static_vision'),
    url(r'^chart/', TemplateView.as_view(template_name='main/static/chart.html'), name='static_chart'),
    url(r'^sponsorship/', TemplateView.as_view(template_name='main/static/sponsorship.html'),
        name='static_sponsorship'),
    url(r'^faq/', TemplateView.as_view(template_name='main/static/faq.html'), name='static_faq'),
]
