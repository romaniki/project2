import datetime


from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django import forms


from .models import User, Listing, Comment, Watchlist, Bid


def index(request):
    listings = Listing.objects.all()
    categories = set([listing.category.capitalize() for listing in listings])
    try:
        wl = Watchlist.objects.get(user=request.user)
        items_num = len(wl.items.all())
        return render(request, "auctions/index.html", {
            "listings": listings,
            "items_num": items_num,
            "categories": categories
        })
    
    except (TypeError, Watchlist.DoesNotExist):
        items_num = 0
        return render(request, "auctions/index.html", {
            "listings": Listing.objects.all(),
            "items_num": items_num,
            "categories": categories,
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

@login_required
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

@login_required
def create(request):
    listings = Listing.objects.all()
    categories = set([listing.category.capitalize() for listing in listings])
    try:
        wl = Watchlist.objects.get(user=request.user)
        items_num = len(wl.items.all())
    except (TypeError, Watchlist.DoesNotExist):
        items_num = 0
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        starting_bid = request.POST["starting_bid"]
        image_url = request.POST["image_url"]
        category = request.POST["category"]
        published_by = request.user
        listing = Listing.objects.create(title=title, 
        description=description, 
        starting_bid=starting_bid, 
        current_price=starting_bid, 
        image_url=image_url, 
        category=category,
        published_by=published_by,
        )
        listing.save()
        return HttpResponseRedirect(reverse("index"))
    return render(request, "auctions/create.html", {
        "items_num": items_num,
        "categories": categories
    })

def listing(request, listing_id):
    listings = Listing.objects.all()
    categories = set([listing.category.capitalize() for listing in listings])
    user = request.user
    if request.user.is_authenticated:
        try:
            wl = Watchlist.objects.get(user=request.user)
            items_num = len(wl.items.all())
        except Watchlist.DoesNotExist:
            items_num = 0
    else:
        items_num = 0
    listing = Listing.objects.get(id=listing_id)
      
    try:
        all_bids = Bid.objects.all().filter(item=listing).order_by('-user_bid')
        # Define the highest bid
        max_bid = all_bids.first().user_bid
        # Define the winner
        winner = all_bids.first().bidder
        
    except AttributeError:
        all_bids = None
        max_bid = listing.starting_bid
        winner = None
    
    # Select all comments for this page
    if Comment.objects.filter(listing=listing).exists():
        comments = Comment.objects.all().filter(listing=listing_id).order_by('-created_on')
    else:
        comments = None
    
    # Update current price
    listing.current_price = max_bid
    listing.save()

    if request.method == "POST":
        
        if "bid" in request.POST:
            user_bid = request.POST["user_bid"]
            if int(user_bid) > listing.current_price:
                listing.current_price = int(user_bid)
                listing.save()
                bid = Bid.objects.create(
                    bidder=user,
                    item=listing,
                    user_bid=user_bid,
                    )
                return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
            else:
                messages.warning(request, f'Your bid must be higher than ${max_bid}')
            
        if "comment" in request.POST:
            text = request.POST["user_comment"]
            comment = Comment.objects.create(
                author=request.user,
                listing=listing,
                text=text,
            )
            messages.info(request, 'Comment has been added')
            return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
            
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "bids": all_bids,
        "max_bid": max_bid,
        "winner": winner,
        "comments": comments,
        "items_num": items_num,
        "categories": categories,
        })

# Add an option to close the user's listing
@login_required
def close(request,listing_id):
    listing = Listing.objects.get(published_by=request.user, id=listing_id)
    listing.is_active = False
    listing.save(update_fields=['is_active'])
    messages.success(request, "You have successfully closed the listing.")
    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

@login_required
def bookmark(request,listing_id):
    username = request.user.username
    listing = Listing.objects.get(id=listing_id)
    if Watchlist.objects.filter(user=request.user, items=listing_id).exists():
        messages.info(request, "This item is already in your watchlist!")
        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
    bookmark, created = Watchlist.objects.get_or_create(user=request.user)
    bookmark.items.add(listing)
    
    try:
        wl = Watchlist.objects.get(user=request.user.id)
        items_num = len(wl.items.all())
    except Watchlist.DoesNotExist:
        items_num = 0
    
    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

def rmbookmark(request, listing_id):
    username = request.user
    listing = Listing.objects.get(id=listing_id)
    bookmark = Watchlist.objects.get(user=request.user, items=listing_id)
    bookmark.items.remove(listing)
    return HttpResponseRedirect(reverse("watchlist", args=(username,)))

@login_required
def watchlist(request, username):
    username = request.user
    listings = Listing.objects.all()
    categories = set([listing.category.capitalize() for listing in listings])
    try:
        wl = Watchlist.objects.get(user=request.user.id)
        items_num = len(wl.items.all())
        return render(request, "auctions/watchlist.html",{
                "items": wl.items.all(),
                "items_num": items_num,
                "categories": categories,
                })
    except Watchlist.DoesNotExist:
        return render(request, "auctions/watchlist.html")

def categories(request):
    try:
        wl = Watchlist.objects.get(user=request.user)
        items_num = len(wl.items.all())
    except (TypeError, Watchlist.DoesNotExist):
        items_num = 0
    listings = Listing.objects.all()
    categories = set([listing.category.capitalize() for listing in listings])
    return render(request, "auctions/categories.html", {
        "categories": categories,
        "items_num": items_num
    })

def category(request, category):
    listings = Listing.objects.all()
    categories = set([listing.category.capitalize() for listing in listings])
    try:
        wl = Watchlist.objects.get(user=request.user)
        items_num = len(wl.items.all())
    except (TypeError, Watchlist.DoesNotExist):
        items_num = 0
    listings = Listing.objects.all().filter(category=category.lower()).order_by('-created_at')
    return render(request, "auctions/category.html", {
        "listings": listings,
        "category": category,
        "categories": categories,
        'items_num': items_num
    })
