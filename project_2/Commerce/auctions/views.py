from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .models import User, Listing, Bid, Comment


def index(request):
    listings = Listing.objects.all()
    return render(request, "auctions/index.html",{
        "listings": listings,
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def create(request):
    if request.method == "POST":

        data = request.POST

        bid = Bid.objects.create(
            bid=float(data["bid"]),
            buyer=request.user
        )

        img_url = data.get("imgURL", "").strip()
        if not img_url:
            img_url = "https://www.svgrepo.com/show/340721/no-image.svg"

        Listing.objects.create(
            title=data["title"],
            description=data["description"],
            starting_bid=bid,
            category=data["category"],
            imgURL=img_url,
            seller=request.user
        )



        return redirect("index")

    return render(request,"auctions/create.html")


def listing(request, listing_id):
    details = get_object_or_404(Listing, pk=listing_id)

    comments = Comment.objects.filter(listing=details).order_by('-com_date')

    if details.active:
        if request.method == "POST":
            action = request.POST.get("action")

            if action == "bid":
                bid = Bid(bid=request.POST.get("bid") , buyer=request.user)
                bid.save()
                details.starting_bid = bid
                details.save()

            if action == "add_comment":
                if not request.user.is_authenticated:
                    return redirect("login")

                content = request.POST.get("comment")
                if content:
                    Comment.objects.create(
                        writer=request.user,
                        content=content,
                        listing=details
                    )
                    return redirect("listing", listing_id=listing_id)


    return render(request, "auctions/listing.html", {
        "details": details,
        "authenticated": request.user.is_authenticated,
        "comments": comments,
    })


def close(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    listing.active = False
    listing.save()
    return redirect("listing", listing_id=listing_id)


def watchlist(request):
    listings = Listing.objects.all()
    watchlist = []

    for listing in listings:
        if request.user in listing.watchlist.all():
            watchlist.append(listing)

    return render(request, "auctions/watchlist.html", {
        "listings": watchlist
    })


def add_watchlist(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    listing.watchlist.add(request.user)
    listing.save()
    return redirect("listing", listing_id=listing_id)


def remove_watchlist(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    listing.watchlist.remove(request.user)
    listing.save()
    return redirect("listing", listing_id=listing_id)


def categories(request):
    listings = Listing.objects.all()

    if request.method == "POST":
        category = request.POST.get("category")
        listings = listings.filter(category=category)


    category_choices = Listing.CATEGORY_CHOICES
    return render(request, "auctions/categories.html", {
        "listings": listings,
        "category_choices": category_choices,
    })