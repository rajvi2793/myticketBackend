# //// rajvi changes for middleware user logged in
import json
from datetime import datetime
from tickety.models import QitApilog, QitCompany, QitCompanycustomer, QitCompanyuser
from tickety.Views.auth_views import authenticate  # Import the authenticate function

class ApiLoggingMiddleware:
    """
    Middleware to log API requests and responses.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if getattr(request, 'disable_logging', False):
            return self.get_response(request)

        # Log request details
        request_data = request.body.decode('utf-8') if request.body else None

        # Authenticate the user using the custom authentication logic
        user = None
        try:
            authenticated_user = authenticate(request)
            user = authenticated_user.email if authenticated_user else "Anonymous"
            urole = authenticated_user.userrole if authenticated_user else "None"
        except Exception as e:
            user = "Unauthorized"
            urole = "None"
            print(f"Authentication failed: {e}")

        cmptransid = None
        if urole == "customer":
            customer = QitCompanycustomer.objects.filter(custemail=user, custisdeleted=0).first()
            if customer:
                cmptransid = customer.companytransid.transid
            else:
                print("Customer data not found")

        elif urole == "company":
            company = QitCompany.objects.filter(companyemail=user, companyisdeleted=0).first()
            if company:
                cmptransid = company.transid
            else:
                print("Company data not found")

        elif urole == "companyuser":
            company_user = QitCompanyuser.objects.filter(cmpuseremail=user, cmpuserisdeleted=0).first()
            if company_user:
                cmptransid = company_user.companytransid.transid
            else:
                print("Company user not found")
 

        filteredRole=None
        if urole == "customer":
            filteredRole ="Customer"
        elif urole=="companyuser":
            filteredRole="User"
        elif urole== "company":
            filteredRole="Company"

        response = self.get_response(request)

        try:
            # Determine the module and view function name
            resolver_match = request.resolver_match
            view_function_name = None
            if resolver_match and resolver_match.func:
                module_path = resolver_match.func.__module__
                view_function_name = module_path.split('.')[-1]

            # Dynamically set log level based on the response status code
            loglevel = "I" if response.status_code < 400 else "E"

            # Log the request and response to the database
            QitApilog.objects.create(
                module=view_function_name if view_function_name else "UnknownModule",
                viewname=request.resolver_match.view_name if request.resolver_match else None,
                methodname=request.method,
                loglevel=loglevel,  # Dynamic log level
                logmessage=f"Request processed with status {response.status_code}",
                jsonpayload=request_data,
                loginuser=user,
                userrole=filteredRole,
                entrydate=datetime.now(),
                cmptransid=cmptransid,
            )
        except Exception as e:
            print(f"Logging failed: {e}")  # Avoid breaking the middleware if logging fails

        return response


# class ApiLoggingMiddleware:
#     """
#     Middleware to log API requests and responses.
#     """
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         # Skip logging for specific views, such as 'get_all_apilogs'
#         if getattr(request, 'disable_logging', False) or (request.resolver_match and request.resolver_match.view_name == 'get_all_apilogs'):
#             return self.get_response(request)

#         # Log request details
#         request_data = request.body.decode('utf-8') if request.body else None

#         # Authenticate the user using the custom authentication logic
#         user = None
#         try:
#             authenticated_user = authenticate(request)
#             user = authenticated_user.email if authenticated_user else "Anonymous"
#             urole = authenticated_user.userrole if authenticated_user else "None"
#         except Exception as e:
#             user = "Unauthorized"
#             urole = "None"
#             print(f"Authentication failed: {e}")

#         cmptransid = None
#         if urole == "customer":
#             customer = QitCompanycustomer.objects.filter(custemail=user, custisdeleted=0).first()
#             if customer:
#                 cmptransid = customer.companytransid.transid
#             else:
#                 print("Customer data not found")

#         elif urole == "company":
#             company = QitCompany.objects.filter(companyemail=user, companyisdeleted=0).first()
#             if company:
#                 cmptransid = company.transid
#             else:
#                 print("Company data not found")

#         elif urole == "companyuser":
#             company_user = QitCompanyuser.objects.filter(cmpuseremail=user, cmpuserisdeleted=0).first()
#             if company_user:
#                 cmptransid = company_user.companytransid.transid
#             else:
#                 print("Company user not found")

#         response = self.get_response(request)

#         try:
#             # Determine the module and view function name
#             resolver_match = request.resolver_match
#             view_function_name = None
#             if resolver_match and resolver_match.func:
#                 module_path = resolver_match.func.__module__
#                 view_function_name = module_path.split('.')[-1]

#             # Dynamically set log level based on the response status code
#             loglevel = "I" if response.status_code < 400 else "E"

#             # Log the request and response to the database, excluding the 'get_all_apilogs' view
#             if request.resolver_match.view_name != 'get_all_apilogs':  # Check if the current view is 'get_all_apilogs'
#                 QitApilog.objects.create(
#                     module=view_function_name if view_function_name else "UnknownModule",
#                     viewname=request.resolver_match.view_name if request.resolver_match else None,
#                     methodname=request.method,
#                     loglevel=loglevel,  # Dynamic log level
#                     logmessage=f"Request processed with status {response.status_code}",
#                     jsonpayload=request_data,
#                     loginuser=user,
#                     userrole=urole,
#                     entrydate=datetime.now(),
#                     cmptransid=cmptransid,
#                 )
#         except Exception as e:
#             print(f"Logging failed: {e}")  # Avoid breaking the middleware if logging fails

#         return response
