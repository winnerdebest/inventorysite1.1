from django.db import models
from decimal import Decimal 
from django.conf import settings
from django.contrib.auth.models import User

# Category Model
class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
# Product Model
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    unit_price = models.DecimalField(max_digits=20, decimal_places=2) # Price per unit
    closing_stock_value = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    stock_balance = models.PositiveIntegerField(default=0, null=True) # Remaining stock
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)

    
    def save(self, *args, **kwargs):
        # Ensure stock_balance is treated as Decimal for multiplication
        self.closing_stock_value = Decimal(self.stock_balance) * self.unit_price
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
    


class ProductEditHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    old_stock_balance = models.PositiveIntegerField()
    new_stock_balance = models.PositiveIntegerField()
    old_unit_price = models.DecimalField(max_digits=100, decimal_places=2)
    new_unit_price = models.DecimalField(max_digits=100, decimal_places=2)
    edited_at = models.DateTimeField(auto_now_add=True)
    edited_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    is_approved = models.BooleanField(default=False)  # To track approval status
    approved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='approver')  # Who approved


    def __str__(self):
        return f"Edit History for {self.product.name} at {self.edited_at}"


#Vendor Model
class Vendor(models.Model):
    name = models.CharField(max_length=255)
    contact_info = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# When a new Purchase is made it is subtracted from the opening balance of the product
# Purchase Model (product bought from vendor)
class Purchase(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    quantity_received = models.PositiveIntegerField()
    date_received = models.DateTimeField(auto_now_add=True)
    amount_received = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # Unit price * quantity_received
    approved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)  # Field to track the user who approved the purchase
    supervisor = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='supervisor_purchases')  #


    coordinator_approved = models.BooleanField(default=False)
    gm_approved = models.BooleanField(default=False)

    coordinator_approver = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name='coordinator_approvals'
    )
    gm_approver = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name='gm_approvals'
    )

def __str__(self):
        return f"Purchase of {self.quantity_received} {self.product.name} from {self.vendor.name} on {self.date_received}"
    

# Stock Movement Model (tracking stock issues and returns,)
# This is also product given to vendors
class StockMovement(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity_issued = models.PositiveIntegerField(default=0)
    quantity_returned = models.PositiveIntegerField(null=True)
    location_received = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Update product stock balance when a stock movement is saved
        if self.quantity_issued > 0:
            if self.product.stock_balance < self.quantity_issued:
                raise ValueError("Insufficient stock balance to issue this quantity.")
            self.product.stock_balance -= self.quantity_issued

        if self.quantity_returned > 0:
            self.product.stock_balance += self.quantity_returned

        # Recalculate closing stock value
        self.product.closing_stock_value = self.product.stock_balance * self.product.unit_price

        # Save the updated product
        self.product.save()

        # Proceed with saving the stock movement
        super().save(*args, **kwargs)

    
    def __str__(self):
            return f"{self.product.name} movement on {self.date}"





class DieselTracker(models.Model):
    date_of_request = models.DateTimeField(auto_now_add=True)
    restocker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='diesel_requests')  # Supervisor
    quantity_requested = models.PositiveIntegerField(default=0)
    quantity_restocked = models.PositiveIntegerField(default=0)
    stock_balance = models.PositiveIntegerField(default=0)  # Updated based on requests/restocks
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='diesel_approvals')  # Inventory Manager
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    purchase_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)  # Unit price * Quantity restocked
    issued_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)  # Unit price * Quantity requested

    def save(self, *args, **kwargs):
        if self.quantity_restocked > 0:
            self.stock_balance += self.quantity_restocked
            self.purchase_value = self.unit_price * self.quantity_restocked
        if self.quantity_requested > 0:
            if self.stock_balance < self.quantity_requested:
                raise ValueError("Insufficient stock to fulfill the request.")
            self.stock_balance -= self.quantity_requested
            self.issued_value = self.unit_price * self.quantity_requested

        super(DieselTracker, self).save(*args, **kwargs)

    def __str__(self):
        return f"Diesel Request on {self.date_of_request}"