from django.shortcuts import render, get_object_or_404, redirect
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Category, Product, Vendor, Purchase, StockMovement, DieselTracker, ProductEditHistory, UserProfile
from django.db import transaction
from django.contrib.auth.models import Group
from django.contrib import messages
from decimal import Decimal
from django.db.models import Q
from .decorators import role_required
from django.contrib.auth import login
from .forms import RegisterForm, PurchaseForm 
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


#Ensure a UserProfile is created whenever a User instance is created.

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

# Registration Page


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()  # Saves the user   
            return redirect("login")  # Redirect to the login page after successful registration
    else:
        form = RegisterForm()
    
    return render(request, "main/register.html", {"form": form})


GROUP_REDIRECTS = {
    "General Manager": 'gm_dashboard',
    "Coordinators": 'coordinator_dashboard',
    "Internal Control": 'internal_control',
    "Inventory Manager": 'inventory_dashboard',
    "Procurement": 'procurement_dashboard',
    "Supervisor": 'supervisor_dashboard',
}

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if not user.is_active:
                messages.error(request, "Your account is inactive. Contact the admin.")
                return redirect('login')

            if hasattr(user, 'userprofile') and not user.userprofile.is_approved:
                messages.error(request, "Your account is pending approval.")
                return redirect('login')

            login(request, user)

            # Redirect based on group
            for group_name, redirect_url in GROUP_REDIRECTS.items():
                if user.groups.filter(name=group_name).exists():
                    return redirect(redirect_url)

            messages.error(request, "User does not belong to a recognized group.")
            return redirect('login')
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, 'main/login.html')


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('login')

# End Of Registration and  Login Page

#Search for supervisors
@login_required
@role_required('Supervisor')  # Adjust role if needed
def search_products(request):
    query = request.GET.get('q', '')  # Search query
    product_results = []

    if query:
        # Search for products
        product_results = Product.objects.filter(
            name__icontains=query
        ) | Product.objects.filter(
            category__name__icontains=query
        )

    # Fetch all categories for the category dropdown
    categories = Category.objects.all()

    context = {
        'query': query,
        'product_results': product_results,
        'categories': categories,
    }

    return render(request, 'supervisor/search_products.html', context)




#Search Algorithm For inventory manager
@login_required
@role_required('Inventory Manager')
def search_purchase(request):
    query = request.GET.get('q', '')
    purchase_results = []
    product_results = []

    if query:
        # Search for purchases
        purchase_results = Purchase.objects.filter(
            request_number__icontains=query
        ) | Purchase.objects.filter(
            product__name__icontains=query
        ) | Purchase.objects.filter(
            product__category__name__icontains=query
        ) | Purchase.objects.filter(
            date_received__icontains=query
        )

        # Search for products
        product_results = Product.objects.filter(
            name__icontains=query
        ) | Product.objects.filter(
            category__name__icontains=query
        )

    context = {
        'query': query,
        'purchase_results': purchase_results,
        'product_results': product_results,
    }
    return render(request, 'inventory_manager/search.html', context)



# This is the Inventory managers view
@login_required
@role_required('Inventory Manager')
def inventory_dashboard(request):
    categories = Category.objects.prefetch_related('product_set').all()
    vendors = Vendor.objects.all()
    purchases = Purchase.objects.select_related('product', 'vendor').all()
    movements = StockMovement.objects.select_related('product').all()

    context = {
        'categories': categories,
        'vendors': vendors,
        'purchases': purchases,
        'movements': movements,
    }
    return render(request, 'inventory_manager/dashboard.html', context)


@login_required
def product_purchases(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    purchases = Purchase.objects.filter(product=product).select_related('vendor')
    stock_movements = StockMovement.objects.filter(product=product)

    # Get unapproved ProductEditHistory entries
    edit_history_entries = product.productedithistory_set.filter(is_approved=False)

    if request.method == "POST":
        # Approving ProductEditHistory entries
        if 'history_id' in request.POST:
            history_id = request.POST.get('history_id')
            history = get_object_or_404(ProductEditHistory, id=history_id)

            if not history.is_approved:  # Approve the edit history only if not already approved
                with transaction.atomic():  # Ensure atomicity of operations
                    # Update ProductEditHistory approval status
                    history.is_approved = True
                    history.approved_by = request.user
                    history.save()

                    # Apply changes to the product
                    product.unit_price = history.new_unit_price
                    product.stock_balance = history.new_stock_balance
                    product.save()  # Save the product with the new values

                messages.success(request, "Product edit history approved successfully!")
            else:
                messages.warning(request, "This product edit history entry is already approved.")

        return redirect('product_purchases', product_id=product_id)

    context = {
        'product': product,
        'purchases': purchases,
        'stock_movements': stock_movements,
        'edit_history_entries': edit_history_entries,  # Pass unapproved history entries to the template
    }

    return render(request, 'inventory_manager/product_purchases.html', context)

@login_required
@role_required('Inventory Manager')
def add_product(request):
    if request.method == "POST":
        product_name = request.POST.get('product_name')
        category_id = request.POST.get('category_id')
        unit_price = Decimal(request.POST['unit_price'])  # Convert to Decimal
        stock_balance = int(request.POST['stock_balance'])
        image = request.FILES.get('image')

        # Check if all required fields are filled
        if not product_name or not category_id or not unit_price:
            messages.error(request, 'All fields are required.')
            return redirect('add_product')

        try:
            # Convert unit_price to Decimal
            unit_price = Decimal(unit_price)
            
            # Get the selected category from Category model
            category = Category.objects.get(id=category_id)

            # Save the new Product
            Product.objects.create(
                name=product_name,
                category=category,
                unit_price=unit_price,
                stock_balance=stock_balance,
                image=image,
            )

            messages.success(request, 'Product added successfully.')
            return redirect('success')

        except Category.DoesNotExist:
            messages.error(request, 'Selected category does not exist.')
            return redirect('add_product')
        except ValueError:
            messages.error(request, 'Unit price must be a valid number.')
            return redirect('add_product')

    # Get all categories to display on the frontend
    categories = Category.objects.all()
    return render(request, 'inventory_manager/add_product.html', {'categories': categories})


@login_required
@role_required('Inventory Manager')
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        unit_price = request.POST.get('unit_price', product.unit_price)
        stock_increment = request.POST.get('stock_increment', 0)

        try:
            # Ensure correct data types
            unit_price = Decimal(unit_price)  # Convert to Decimal
            stock_increment = int(stock_increment)  # Convert to int

            # Update the product's unit price and stock balance
            product.unit_price = unit_price
            product.stock_balance += stock_increment  # Add to the stock balance
            product.save()

            messages.success(request, "Product updated successfully!")
            return redirect('inventory_dashboard')  # Redirect to your dashboard or product list

        except (ValueError, TypeError) as e:
            messages.error(request, "Invalid input for price or stock increment.")
            return redirect('edit_product', product_id=product.id)

    return render(request, 'inventory_manager/edit_product.html', {'product': product})


@login_required
@role_required('Inventory Manager')
def add_category(request):
    if request.method == "POST":
        category_name = request.POST.get('category_name')

        # Ensure category name is provided
        if not category_name:
            messages.error(request, 'Category name is required.')
            return redirect('add_category')

        # Save the new Category
        Category.objects.create(name=category_name)
        messages.success(request, 'Category added successfully.')
        return redirect('success')
    
    return render(request, 'inventory_manager/add_category.html')


@login_required
@role_required('Inventory Manager')
def success(request):
    return render(request, 'inventory_manager/success.html')


@login_required
@role_required('Inventory Manager')
def add_stock_movement(request):
    if request.method == "POST":
        product_id = request.POST['product']
        quantity_issued = int(request.POST.get('quantity_issued', 0))
        quantity_returned = int(request.POST.get('quantity_returned', 0))
        location_received = request.POST['location_received']

        # Fetch the product instance
        product = Product.objects.get(id=product_id)

        # Create the stock movement record
        StockMovement.objects.create(
            product=product,
            quantity_issued=quantity_issued,
            quantity_returned=quantity_returned,
            location_received=location_received
        )

        messages.success(request, "Stock movement added successfully!")
        return redirect('add_stock_movement')
    
    product_id = request.GET.get('product', None)
    products = Product.objects.all()
    selected_product = Product.objects.get(id=product_id) if product_id else None

    products = Product.objects.all()
    return render(request, 'inventory_manager/add_stock_movement.html', {'products': products, 'selected_product': selected_product,})
# End of Inventory Managers View

# Supervisor  View

@login_required
@role_required('Supervisor')
def supervisor_dashboard(request):
    # Fetch all products
    categories = Category.objects.prefetch_related('product_set').all()

    # Filter purchases by approval status and supervisor
    pending_requests = Purchase.objects.filter(supervisor=request.user, gm_approved=False)
    approved_requests = Purchase.objects.filter(supervisor=request.user, gm_approved=True)


    


    context = {
        'categories': categories,
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
        }


    return render(request, 'supervisor/dashboard.html', context)


def request_purchase(request, product_id):
    product = get_object_or_404(Product, id=product_id)  # Get the product by ID
    vendors = Vendor.objects.all()  # Get all vendors
    
    if request.method == "POST":
        # Create a purchase request from the form data
        quantity_received = int(request.POST.get('quantity_received'))
        vendor_id = request.POST.get('vendor')

        # Create the Purchase object
        purchase = Purchase(
            product=product,  # Associate the product with the purchase
            supervisor=request.user,  # Associate the logged-in supervisor
            vendor_id=vendor_id,  # Get the selected vendor
            quantity_received=quantity_received,  # Set the received quantity# Set approval status to false by default
        )
        
        purchase.save()  # Save the purchase request
        messages.success(request, "Purchase request submitted successfully!")
        return redirect('supervisor_dashboard')  # Redirect to the supervisor page or desired page

    # For GET request, create an empty form context
    form = PurchaseForm()  # Initialize an empty form

    context = {
        'form': form,
        'product': product,
        'vendors': vendors,  # Pass the list of vendors to the context
    }
    return render(request, 'supervisor/request_purchase.html', context)



# End of Supervisor Views



#@login_required
#@role_required('General Manager') 
def general_manager_dashboard(request):
    # Fetch all the transactions
    purchases = Purchase.objects.select_related('product', 'vendor', 'approved_by').all()
    stock_movements = StockMovement.objects.select_related('product').all()

    context = {
        'purchases': purchases,
        'stock_movements': stock_movements,
    }

    return render(request, 'general_manager/dashboard.html', context)






def manager_dashboard(request):
    return render(request, 'dashboard/manager_dashboard.html')





# Procurement Dashboard

@login_required
@role_required('Procurement')
def procurement_dashboard(request):
    categories = Category.objects.prefetch_related('product_set').all()
    vendors = Vendor.objects.all()
    purchases = Purchase.objects.select_related('product', 'vendor').all()


    context = {
        'categories': categories,
        'vendors': vendors,
        'purchases': purchases,
    }
    return render(request, 'procurement/dashboard.html', context)




def procurement_edit_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    if request.method == 'POST':
        # Get the new unit_price and stock increment values from the form
        unit_price = request.POST.get('unit_price')  # new unit price
        stock_increment = int(request.POST.get('stock_increment', 0))  # new stock increment

        # Record the history without updating the product
        if unit_price != str(product.unit_price) or stock_increment != 0:
            # Create a new history record before saving changes
            ProductEditHistory.objects.create(
                product=product,
                old_stock_balance=product.stock_balance,

                new_stock_balance=product.stock_balance + stock_increment,
                old_unit_price=product.unit_price,
                new_unit_price=unit_price,
                edited_by=request.user,  # Set the user if logged in
            )

        # Redirect to another view (e.g., product list)
        return redirect('procurement_dashboard')  # Update this to the correct URL name for your product list page

    return render(request, 'procurement/add_balance.html', {'product': product})


# End Of Procurement Dashboard


#Coordinators Dashboard
@login_required
@role_required('Coordinators')
def coordinator_dashboard(request):
    categories = Category.objects.prefetch_related('product_set').all()
    vendors = Vendor.objects.all()
    purchases = Purchase.objects.select_related('product', 'vendor').all()


    context = {
        'categories': categories,
        'vendors': vendors,
        'purchases': purchases,
    }
    return render(request, 'coordinator/dashboard.html', context)

@login_required
@role_required('Coordinators')
def coordinator_approve(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    purchases = Purchase.objects.filter(product=product).select_related('vendor')

    if 'purchase_id' in request.POST:
        purchase_id = request.POST.get('purchase_id')
        purchase = get_object_or_404(Purchase, id=purchase_id)

        if not purchase.coordinator_approved:  # Approve only if not already approved by the Coordinator
            with transaction.atomic():  # Ensure atomicity
                purchase.coordinator_approved = True
                purchase.coordinator_approver = request.user
                purchase.save()

            messages.success(request, "Purchase approved by Coordinator successfully!")
        else:
            messages.warning(request, "This purchase is already approved by the Coordinator.")

        return redirect('coordinator_approve', product_id=product_id)

    context = {
        'product': product,
        'purchases': purchases,
    }
    return render(request, 'coordinator/approve.html', context)
        

@login_required
@role_required('General Manager')
def gm_dashboard(request):
    categories = Category.objects.prefetch_related('product_set').all()
    vendors = Vendor.objects.all()
    purchases = Purchase.objects.select_related('product', 'vendor').all()
    movements = StockMovement.objects.select_related('product').all()

    context = {
        'categories': categories,
        'vendors': vendors,
        'purchases': purchases,
        'movements': movements,
    }
    return render(request, 'GM/dashboard.html', context)



@login_required
@role_required('General Manager')
def gm_approve(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    purchases = Purchase.objects.filter(product=product).select_related('vendor')
    stock_movements = StockMovement.objects.filter(product=product)

    # Get unapproved ProductEditHistory entries
    edit_history_entries = product.productedithistory_set.filter(is_approved=False)

    if 'purchase_id' in request.POST:
        purchase_id = request.POST.get('purchase_id')
        purchase = get_object_or_404(Purchase, id=purchase_id)

        if purchase.coordinator_approved and not purchase.gm_approved:  # Ensure Coordinator approved first
            with transaction.atomic():  # Ensure atomicity
                purchase.gm_approved = True
                purchase.gm_approver = request.user
                purchase.save()

                # Perform stock calculations after final GM approval
                product.stock_balance -= purchase.quantity_received
                product.closing_stock_value = product.stock_balance * product.unit_price
                product.save()

            messages.success(request, "Purchase fully approved by General Manager!")
        elif not purchase.coordinator_approved:
            messages.warning(request, "Coordinator approval is required before GM approval.")
        else:
            messages.warning(request, "This purchase is already approved by the General Manager.")

        return redirect('gm_approve', product_id=product_id)

    context = {
        'product': product,
        'purchases': purchases,
        'stock_movements': stock_movements,
    }
    return render(request, 'gm/detail.html', context)





@login_required
@role_required('Internal Control')
def internal_control(request):
    categories = Category.objects.prefetch_related('product_set').all()
    vendors = Vendor.objects.all()
    purchases = Purchase.objects.select_related('product', 'vendor').all()
    movements = StockMovement.objects.select_related('product').all()

    context = {
        'categories': categories,
        'vendors': vendors,
        'purchases': purchases,
        'movements': movements,
    }
    return render(request, 'internal_control/dashboard.html', context)


@login_required
@role_required('Internal Control')
def approve_users(request):
    # Fetch all users, both approved and unapproved
    all_users = UserProfile.objects.all()

    if request.method == "POST":
        user_profile_id = request.POST.get("user_profile_id")
        action = request.POST.get("action")

        # Get the user profile object
        user_profile = get_object_or_404(UserProfile, id=user_profile_id)

        if action == "approve":
            user_profile.is_approved = True
            user_profile.save()
            messages.success(request, f"User {user_profile.user.username} has been approved.")
        elif action == "reject":
            # Set the user profile as unapproved (not deleted)
            user_profile.is_approved = False
            user_profile.save()
            messages.success(request, f"User {user_profile.user.username} has been unapproved.")

        return redirect("approve_users")

    # Pass all users to the template
    context = {
        "all_users": [
            {
                "id": profile.id,
                "username": profile.user.username,
                "email": profile.user.email,
                "groups": profile.user.groups.all(),
                "is_approved": profile.is_approved,
            }
            for profile in all_users
        ]
    }

    return render(request, "internal_control/approve.html", context)



@login_required
@role_required('Internal Control') 
def internal_details(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    purchases = Purchase.objects.filter(product=product).select_related('vendor')
    stock_movements = StockMovement.objects.filter(product=product)

    # Get unapproved ProductEditHistory entries
    edit_history_entries = product.productedithistory_set.filter(is_approved=False)

    context = {
        'product': product,
        'purchases': purchases,
        'stock_movements': stock_movements,
    }
    return render(request, 'internal_control/detail.html', context)

