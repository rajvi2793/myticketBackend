from rest_framework.decorators import api_view, authentication_classes, permission_classes
from tickety.models import QitCompany, QitCompanycustomer,QitCatsubcatmapping,QitTicketcategory
from django.shortcuts import get_object_or_404
from tickety.Views import auth_views
from rest_framework.response import Response
from rest_framework import status


@api_view(['GET'])
@authentication_classes([auth_views.CustomAuthentication])  # Apply custom authentication
def get_categories_with_subcategories(request):
    # Fetch companyid and custid from query parameters
    companyid = request.query_params.get('companyid')
    custid = request.query_params.get('custid')

    # Ensure company and customer exist
    company = get_object_or_404(QitCompany, transid=companyid)
    customer = get_object_or_404(QitCompanycustomer, transid=custid)

    # Fetch category-subcategory mappings for the given company and customer
    mappings = QitCatsubcatmapping.objects.filter(company=company, customer=customer)

    # Initialize the response data list
    category_subcategory_mappings = []

    # Iterate through each mapping to group them by category
    for mapping in mappings:
        # Check if the category already exists in the response data
        category_data = next((item for item in category_subcategory_mappings if item['category_id'] == mapping.category.transid), None)

        if not category_data:
            # If the category is not in the response data, create a new entry for it
            category_data = {
                "category_id": mapping.category.transid,
                "category_name": mapping.category.ticketcategoryname,
                "subcategories": []
            }
            category_subcategory_mappings.append(category_data)

        # Add the subcategory data to the category's subcategory list
        if mapping.subcategory:
            category_data['subcategories'].append({
                # "category_id": mapping.category.transid,
                "subcategory_id": mapping.subcategory.transid,
                "subcategory_name": mapping.subcategory.ticketsubcatname
            })
        else:
            # If there is no subcategory, add a null value
            category_data['subcategories'].append(None)

    return Response({"category_subcategory_mappings": category_subcategory_mappings})




# # display all other field also
# @api_view(['GET']) 
# @authentication_classes([auth_views.CustomAuthentication])  # Apply custom authentication
# def get_all_ticket_categories_with_subcategories(request):
#     try:
#         # Retrieve all ticket categories with related subcategories
#         ticket_categories = QitTicketcategory.objects.prefetch_related('qitticketsubcategory_set').all()
        
#         # Prepare response data
#         response_data = []
#         for category in ticket_categories:
#             subcategories = category.qitticketsubcategory_set.all()
#             subcategory_list = [
#                 {
#                     "transid": sub.transid,
#                     "ticketsubcatname": sub.ticketsubcatname,
#                     "ticketsubiddeleted": sub.ticketsubiddeleted,
#                     "entry_date": sub.entry_date,
#                     "update_date": sub.update_date,
#                     "companytransid": sub.companytransid_id,
#                     "ticketcategorytransid": sub.ticketcategorytransid_id,
#                 }
#                 for sub in subcategories
#             ]
            
#             response_data.append({
#                 "transid": category.transid,
#                 "ticketcategoryname": category.ticketcategoryname,
#                 "companytransid": category.companytransid_id,
#                 "ticketisdeleted": category.ticketisdeleted,
#                 "entry_date": category.entry_date,
#                 "update_date": category.update_date,
#                 "subcategories": subcategory_list  # Subcategories array inside each category
#             })
        
#         # Return response with structured data
#         return Response({'message': 'All ticket categories with subcategories retrieved successfully', 'data': response_data}, status=status.HTTP_200_OK)

#     except Exception as e:
#         # Handle errors
#         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




# data are displaying from category and sub category tables
@api_view(['GET'])  
@authentication_classes([auth_views.CustomAuthentication])  # Apply custom authentication
def get_all_ticket_categories_with_subcategories(request):
    try:
        # Get company ID and customer ID from query parameters
        company_id = request.query_params.get('company_id')
        customer_id = request.query_params.get('customer_id')

        if not company_id or not customer_id:
            return Response({'error': 'Both Company ID and Customer ID are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve ticket categories for the specified company
        ticket_categories = QitTicketcategory.objects.filter(companytransid=company_id).prefetch_related('qitticketsubcategory_set')

        # Prepare response data with only required fields
        response_data = []
        for category in ticket_categories:
            subcategories = category.qitticketsubcategory_set.all()
            subcategory_list = []
            category_selected = False
            
            # Loop through each subcategory and check if it is selected for the customer
            for sub in subcategories:
                # Check if this category-subcategory pair is mapped to the given customer
                mapping = QitCatsubcatmapping.objects.filter(
                    company__transid=company_id,
                    customer__transid=customer_id,
                    category=category,
                    subcategory=sub
                ).first()
                
                # If mapping exists and is selected, return True, otherwise False
                selected = mapping.selected == 'True' if mapping else False

                if selected:  # If any subcategory is selected, mark the category as selected
                    category_selected = True
                
                subcategory_list.append({
                    "transid": sub.transid,
                    "ticketsubcatname": sub.ticketsubcatname,
                    "selected": selected  # Display the selection status for the customer
                })
            
            response_data.append({
                "transid": category.transid,
                "ticketcategoryname": category.ticketcategoryname,
                "subcategories": subcategory_list,  # Include selection status in subcategories
                "selected": category_selected, 
            })
        
        # Return response with structured data
        return Response({'message': 'All ticket categories with subcategories retrieved successfully', 'data': response_data}, status=status.HTTP_200_OK)

    except Exception as e:
        # Handle errors
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
