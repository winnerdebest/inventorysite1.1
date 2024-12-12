from django.contrib import admin
from .models import Category, Product, Vendor, Purchase, StockMovement, DieselTracker, ProductEditHistory, UserProfile


admin.site.register(UserProfile)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Vendor)
admin.site.register(Purchase)
admin.site.register(StockMovement)
admin.site.register(DieselTracker)
admin.site.register(ProductEditHistory)

# Fix procurement admin TO add products and unit price(Done)
# The approval is first the Cordinator is after the supervisor(Done)
# If the transaction is higher than 1 million send to managing director
# So design the MD view to be able to view all products and their Transactions
# So design the GM view to be able to view all products and their Transactions