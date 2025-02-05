from rest_framework.decorators import api_view, authentication_classes, permission_classes
from tickety.models import QitCompany, QitCompanycustomer, QitTicketcategory, QitTicketsubcategory,QitCatsubcatmapping
from django.shortcuts import get_object_or_404
from tickety.Views import auth_views
from rest_framework.response import Response
from datetime import datetime

# @api_view(['POST'])
# @authentication_classes([auth_views.CustomAuthentication])  # Apply custom authentication
# def save_category_subcategory_mapping(request):
#     companyid = request.data.get('companyid')
#     custid = request.data.get('custid')
#     categoryids = request.data.get('categoryid', [])
#     subcategoryids = request.data.get('subcategoryid', [])

#     # Ensure company and customer exist
#     company = get_object_or_404(QitCompany, transid=companyid)
#     customer = get_object_or_404(QitCompanycustomer, transid=custid)

#     mappings_to_create = []

#     for categoryid in categoryids:
#         category = get_object_or_404(QitTicketcategory, transid=categoryid)

#         # Fetch only the subcategories that belong to the current category
#         related_subcategories = QitTicketsubcategory.objects.filter(
#             transid__in=subcategoryids, ticketcategorytransid=category
#         )

#         # Check if an existing NULL mapping exists
#         existing_null_mapping = QitCatsubcatmapping.objects.filter(
#             company=company, customer=customer, category=category, subcategory=None
#         ).first()

#         if not related_subcategories.exists():  # If no subcategories exist, insert NULL subcategory
#             if not existing_null_mapping:  # Only insert if NULL mapping does not exist
#                 mappings_to_create.append(QitCatsubcatmapping(
#                     company=company,
#                     customer=customer,
#                     category=category,
#                     subcategory=None,  # No subcategory
#                     entry_date=datetime.now(),
#                     update_date=datetime.now()
#                 ))
#         else:
#             # If NULL mapping exists, delete it before adding new subcategory mappings
#             if existing_null_mapping:
#                 existing_null_mapping.delete()

#             for subcategory in related_subcategories:
#                 # Check if the mapping already exists
#                 existing_mapping = QitCatsubcatmapping.objects.filter(
#                     company=company,
#                     customer=customer,
#                     category=category,
#                     subcategory=subcategory
#                 ).exists()

#                 if not existing_mapping:
#                     mappings_to_create.append(QitCatsubcatmapping(
#                         company=company,
#                         customer=customer,
#                         category=category,
#                         subcategory=subcategory,
#                         entry_date=datetime.now(),
#                         update_date=datetime.now()
#                     ))

#     # Bulk create new mappings
#     if mappings_to_create:
#         QitCatsubcatmapping.objects.bulk_create(mappings_to_create)

#     return Response({"message": "Category-Subcategory mappings saved successfully."}, status=201)

@api_view(['POST'])
@authentication_classes([auth_views.CustomAuthentication])  # Apply custom authentication
def save_category_subcategory_mapping(request):
    companyid = request.data.get('companyid')
    custid = request.data.get('custid')
    categoryids = request.data.get('categoryid', [])
    subcategoryids = request.data.get('subcategoryid', [])

    # Ensure company and customer exist
    company = get_object_or_404(QitCompany, transid=companyid)
    customer = get_object_or_404(QitCompanycustomer, transid=custid)

    # First, mark all existing mappings for the company and customer as 'not selected'
    # This only resets mappings that are not included in the current request
    QitCatsubcatmapping.objects.filter(company=company, customer=customer).exclude(
        category__transid__in=categoryids,
        subcategory__transid__in=subcategoryids
    ).update(selected='False')

    mappings_to_create = []

    for categoryid in categoryids:
        category = get_object_or_404(QitTicketcategory, transid=categoryid)

        # Fetch only the subcategories that belong to the current category
        related_subcategories = QitTicketsubcategory.objects.filter(
            transid__in=subcategoryids, ticketcategorytransid=category
        )

        # Check if an existing NULL mapping exists
        existing_null_mapping = QitCatsubcatmapping.objects.filter(
            company=company, customer=customer, category=category, subcategory=None
        ).first()

        if not related_subcategories.exists():  # If no subcategories exist, insert NULL subcategory
            if not existing_null_mapping:  # Only insert if NULL mapping does not exist
                mappings_to_create.append(QitCatsubcatmapping(
                    company=company,
                    customer=customer,
                    category=category,
                    subcategory=None,  # No subcategory
                    entry_date=datetime.now(),
                    update_date=datetime.now(),
                    selected='False'  # Mark as not selected
                ))
        else:
            # If NULL mapping exists, delete it before adding new subcategory mappings
            if existing_null_mapping:
                existing_null_mapping.delete()

            for subcategory in related_subcategories:
                # Check if the mapping already exists
                existing_mapping = QitCatsubcatmapping.objects.filter(
                    company=company,
                    customer=customer,
                    category=category,
                    subcategory=subcategory
                ).first()

                if existing_mapping:
                    # If the mapping exists, update its selected status to True
                    existing_mapping.selected = 'True'
                    existing_mapping.update_date = datetime.now()
                    existing_mapping.save()
                else:
                    # If the mapping does not exist, create a new one with selected=True
                    mappings_to_create.append(QitCatsubcatmapping(
                        company=company,
                        customer=customer,
                        category=category,
                        subcategory=subcategory,
                        entry_date=datetime.now(),
                        update_date=datetime.now(),
                        selected='True'  # Mark as selected
                    ))

    # Bulk create new mappings
    if mappings_to_create:
        QitCatsubcatmapping.objects.bulk_create(mappings_to_create)

    return Response({"message": "Category-Subcategory mappings saved successfully."}, status=201)
