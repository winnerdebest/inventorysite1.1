from django.urls import path 
from . import views 

urlpatterns = [
    # Login and Log out URLS
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('search/', views.search_purchase, name='search_purchase'),
    
    path('general_manager_dashboard/', views.general_manager_dashboard, name='general_manager_dashboard'),

    # Inventory Manager URLs
    path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('inventory_dashboard/', views.inventory_dashboard, name='inventory_dashboard'),
    path('register/', views.register, name='register'),
    path('add_product/', views.add_product, name='add_product'),
    path('add_category/', views.add_category, name='add_category'),
    path('add_stock_movement/', views.add_stock_movement, name='add_stock_movement'),
    path('success/', views.success, name='success'),
    path('product/<int:product_id>/purchases/', views.product_purchases, name='product_purchases' ),
    # End of Inventory Managers Page

    # Supervisors Page
    path('supervisor_dashboard/', views.supervisor_dashboard, name='supervisor_dashboard'),
    path('request_purchase/<int:product_id>/', views.request_purchase, name='request_purchase'),
    # End of Supervisors Page


    # Procurement Page
    path('product/<int:product_id>/edit/', views.procurement_edit_product, name='procurement_edit_product'),
    path('procurement_dashboard/', views.procurement_dashboard, name='procurement_dashboard'),
    # Coordinators URLS
    path('coordinator_dashboard/', views.coordinator_dashboard, name='coordinator_dashboard'),
    path('product/<int:product_id>/', views.coordinator_approve, name='coordinator_approve'),


    path('gm_dashboard/', views.gm_dashboard, name='gm_dashboard'),
    path('gm_approve/<int:product_id>/', views.gm_approve, name='gm_approve'),
    # Internal Control
    path('approve_users/', views.approve_users, name='approve_users'),
    path('internal_control/', views.internal_control, name="internal_control"),
    path('internal_details/<int:product_id>/', views.internal_details, name="internal_details")



]
    

