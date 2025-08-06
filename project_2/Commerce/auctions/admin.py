from django.contrib import admin

from auctions.models import User, Listing, Comment, Bid

# Register your models here.

admin.site.register(User)
admin.site.register(Listing)
admin.site.register(Comment)
admin.site.register(Bid)