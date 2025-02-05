from django.contrib import admin
from django.urls import path
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from tickety.Views.apiLogView import get_all_apilogs


# Company's Route
from tickety.Views.Company.SaveCompany import save_company
from tickety.Views.Company.EditCompany import edit_company_by_email
from tickety.Views.Company.DisplayCompany import get_all_companies,get_company_by_email


# CompanyUser's Routes
from tickety.Views.CompanyUser.DisplayCompanyUser import get_all_users,get_user_by_usercode
from tickety.Views.CompanyUser.SaveCompanyUser import save_company_user
from tickety.Views.CompanyUser.DeleteCompanyUser import delete_company_user
from tickety.Views.CompanyUser.EditCompanyUser import edit_company_user
from tickety.Views.CompanyUser.GenerateUserCode import generate_user_code
from tickety.Views.CompanyUser.TooglingStatus import toggle_company_user_status
from tickety.Views.CompanyUser.UpdatePassReq import update_passwordreq_user


# Authentication's Routes
from tickety.Views.UserAuthentication.Authentication import LoginView,forgot_user_check,secure_view


# Customer's Routes
from tickety.Views.customer.SaveCustomer import save_customer
from tickety.Views.customer.DeleteCustomer import delete_customer
from tickety.Views.customer.DisplayCustomers import get_customer,get_customer_by_code
from tickety.Views.customer.EditCustomer import edit_customer
from tickety.Views.customer.GenerateCustomerCode import generate_code
from tickety.Views.customer.TooglingStatus import toggle_customer_status
from tickety.Views.customer.UpdatePassReq import update_passwordreq


#   Ticket's Routes
from tickety.Views.Tickets.SaveTickets import save_ticket
from tickety.Views.Tickets.DisplayTicketsByCustomer import get_tickets_by_customer
from tickety.Views.Tickets.DisplayTickets import get_all_tickets,get_ticket_by_code
from tickety.Views.Tickets.TooglingTicketStatus import toggle_ticket_status


#   OTP's Route
from tickety.Views.OTP.GenerateOTP import generate_otp
from tickety.Views.OTP.VerifyOTP import verify_otp
from tickety.Views.OTP.UpdatePassword import verify_otp_and_update_password
from tickety.Views.OTP.ResendOTP import resend_otp


#   Tickets Activitie's Route
from tickety.Views.TicketActivities.SaveActivities import create_ticket_activity
from tickety.Views.TicketActivities.DisplayActivities import ticket_activities_list,ticket_activities_list_by_ticketcode


#   Ticket Category's Route
from tickety.Views.TicketCategory.DisplayCategory import get_all_ticket_categories
from tickety.Views.TicketCategory.SaveCategory import save_ticket_category
from tickety.Views.TicketCategory.EditCategory import edit_ticket_category
from tickety.Views.TicketCategory.DeleteCategory import delete_ticket_category


#   Ticket SubCategory's Route
from tickety.Views.TicketSubCategory.SaveSubCategory import save_ticket_subcategory
from tickety.Views.TicketSubCategory.DisplaySubCategory import get_all_ticket_subcategories,get_ticket_subcategory_by_transid
from tickety.Views.TicketSubCategory.EditSubCategory import edit_ticket_subcategory
from tickety.Views.TicketSubCategory.DeleteSubCategory import delete_ticket_subcategory_by_transid


#   Ticket TimeSpent's Route
from tickety.Views.TicketTimeSpent.SaveTimeSpent import save_QitTicketspent
from tickety.Views.TicketTimeSpent.DisplayTimeSpent import get_ticket_timespent
from tickety.Views.TicketTimeSpent.EditTimeSpent import update_ticket_time_spent
from tickety.Views.TicketTimeSpent.DeleteTimeSpent import delete_ticket_time_spent


#   Ticket Note's Route
from tickety.Views.TicketNotes.SaveNotes import save_QitTicketnotes
from tickety.Views.TicketNotes.EditNotes import edit_QitTicketnotes
from tickety.Views.TicketNotes.DeleteNotes import delete_QitTicketnote
from tickety.Views.TicketNotes.DisplayNotes import get_all_ticket_notes


#   Notification's Route
from tickety.Views.Notification.DisplayNotification import get_notifications
from tickety.Views.Notification.NotificationStatus import update_notification_status


# from tickety.Views.auth_views import TokenRefreshView
from tickety.Views.refreshtoken import TokenRefreshView

#   Configuration's Route
from tickety.Views.ConfigurationEmail.CreateConfiguration import create_configuration
from tickety.Views.ConfigurationEmail.FilterConfiguration import filter_configuration_by_company

from tickety.Views.CategorySubCategoryMapping.getCategorySubCatMap import get_categories_with_subcategories,get_all_ticket_categories_with_subcategories
from tickety.Views.CategorySubCategoryMapping.SaveCategorySubCatMap import save_category_subcategory_mapping


from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    # Authentication Routes
    
    path('admin/', admin.site.urls),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/forgotusercheck/', forgot_user_check,name='ForgotUserCheckView'),
    path('api/secure/', secure_view,name='SecureView'),


    # OTP-related routes
    path('api/generate-otp/', generate_otp, name='generate_otp'),
    path('api/verify-otp/', verify_otp, name='verify_otp'),
    path('api/reset-password/', verify_otp_and_update_password, name='reset_password'),


    # Company
    path('api/save-company/', save_company, name='save_company'),
    path('api/get_all_companies/', get_all_companies, name='get_all_companies'),  # Endpoint to get all companies
    path('api/company_by_email/', get_company_by_email, name='get_company_by_email'),
    path('api/edit_company_by_email/<str:companyemail>/', edit_company_by_email, name='edit_company_by_email'),


    # comapny user routes
    path('api/generate_user_code/', generate_user_code, name='generate_user_code'),
    path('api/save-company-user/', save_company_user, name='save_company_user'),
    path('api/get_all_users/', get_all_users, name='get_all_users'),  # For getting all users
    path('api/users/<str:usercode>/', get_user_by_usercode, name='get_user_by_usercode'),  # For getting a user by usercode
    path('api/toggle_company_user_status/', toggle_company_user_status, name='toggle_company_user_status'),
    path('api/update-passwordreq_user/', update_passwordreq_user, name='update_passwordreq_user'),
    path('api/edit_company_user/<str:cmpusercode>/', edit_company_user, name='edit_company_user'),
    path('api/delete_company_user/<str:cmpusercode>/', delete_company_user, name='delete_company_user'),


    # customer routes
    path('api/generate_code/', generate_code, name='generate_customer_code'),
    path('api/save-customer/', save_customer, name='save_customer'),
    path('api/get_customer/', get_customer, name='get_customer'),
    path('api/customers/<str:custcode>/', get_customer_by_code, name='get_customer_by_code'),  # For specific customer
    path('api/customer/edit/<str:custcode>/', edit_customer, name='edit_customer'),
    path('api/customer/delete/<str:custcode>/', delete_customer, name='delete_customer'),
    path('api/customer/toggle_customer_status/', toggle_customer_status, name='toggle_customer_status'),
    path('api/update-passwordreq/', update_passwordreq, name='update-passwordreq'),


    # Ticket-related routes
    path('api/save_ticket_category/', save_ticket_category, name='save_ticket_category'),
    path('api/ticket_categories/', get_all_ticket_categories, name='get_all_ticket_categories'),
    path('api/ticket_category/edit/<int:transid>/', edit_ticket_category, name='edit_ticket_category'),
    path('api/delete_ticket_category/<int:category_id>/', delete_ticket_category, name='delete_ticket_category'),


    # TicketSubCategory-related routes
    path('api/save_ticket_subcategory/', save_ticket_subcategory, name='save_ticket_subcategory'),
    path('api/ticket_subcategories/', get_all_ticket_subcategories, name='get_all_ticket_subcategories'),
    path('api/edit_ticket_subcategory/<int:transid>/', edit_ticket_subcategory, name='edit_ticket_subcategory'),
    path('api/get_ticket_subcategory/<int:transid>/', get_ticket_subcategory_by_transid, name='get_ticket_subcategory_by_transid'),
    path('api/delete_ticket_subcategory/<int:transid>/', delete_ticket_subcategory_by_transid, name='delete_ticket_subcategory_by_transid'),


    #   Ticket-related routes
    path('api/save_ticket/', save_ticket, name='save_ticket'),
    path('api/tickets/', get_all_tickets, name='get_all_tickets'),
    path('api/tickets/<str:ticketcode>/', get_ticket_by_code, name='get_ticket_by_code'),
    path('api/toggle_ticket_status/', toggle_ticket_status, name='toggle_ticket_status'),
    path('api/get_tickets_by_customer/', get_tickets_by_customer, name='get_tickets_by_customer'),


    #   TicketActivity-related routes
    path('api/ticket_activities/', ticket_activities_list, name='ticket_activities_list'),
    path('api/save_ticket_activity/', create_ticket_activity, name='create_ticket_activity'),
    path('api/tickets/activities/<str:ticketcode>/', ticket_activities_list_by_ticketcode, name='ticket_activities_list_by_ticketcode'),

    
    # Ticket notes routes
    path('api/ticket-note/', save_QitTicketnotes, name='create_ticket_note'),
    path('api/ticket-note/<int:transid>/', edit_QitTicketnotes, name='edit_ticket_note'),
    path('api/ticket-notes/', get_all_ticket_notes, name='get_all_ticket_notes'),
    path('api/delete_ticketnote/<int:transid>/', delete_QitTicketnote, name='delete_ticketnote'),


    # Ticket time spent routes
    path('api/save_ticket_time_spent/', save_QitTicketspent, name='save_ticket_time_spent'),
    path('api/update-ticket-time-spent/<int:pk>/', update_ticket_time_spent, name='update_ticket_time_spent'),
    path('api/delete-ticket-time-spent/<int:pk>/', delete_ticket_time_spent, name='delete_ticket_time_spent'),
    path('api/ticket-timespent/<int:transid>/', get_ticket_timespent, name='get_ticket_timespent'),


    #Notification
    path('api/get-notifications/', get_notifications, name='get_notifications'),
    path('api/update_notification_status/', update_notification_status, name='update_notification_status'),


    # api logs
    path('api/get_all_apilogs/',get_all_apilogs,name='get_all_apilogs'),
    path('api/get_all_apilogs/<int:cmptransid>/',get_all_apilogs,name='get_all_apilogs'),


    #configuration email:
    path('api/create_configuration/', create_configuration, name='create_configuration'),
    path('api/filter-configurations/<int:company_transid>/', filter_configuration_by_company, name='filter_configuration_by_company'),

    path('api/category-subcategory-mapping/', get_categories_with_subcategories, name='category-subcategory-mapping'),
    path('api/get_categories_with_subcategories/', get_all_ticket_categories_with_subcategories, name='get_all_ticket_categories_with_subcategories'),
    path('api/Save-category-subcategory-mapping/', save_category_subcategory_mapping, name='insert_categories_with_subcategories'),


]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

