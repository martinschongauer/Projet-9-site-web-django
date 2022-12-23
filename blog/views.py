from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required

from itertools import chain
from django.db.models import CharField, Value

from blog.models import User, UserFollows, Ticket, Review
from . import forms


def index(request):
    message = ''

    if request.method == 'POST':
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['pass_word'],
            )
            if user is not None:
                login(request, user)
                return redirect("flux")
            else:
                message = 'Identifiants invalides.'

    return render(request, 'blog/index.html',
                  {'css_name': 'blog/index.css',
                   'page_title': 'LITReview - Connexion',
                   'message': message})


@login_required
def user_logout(request):
    logout(request)
    return redirect("index")


def subscribe(request):
    form = forms.SignupForm()
    if request.method == 'POST':
        form = forms.SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("index")

    return render(request, 'blog/subscribe.html',
                  {'css_name': 'blog/index.css',
                   'page_title': 'LITReview - Subscribe',
                   'form': form})


def check_my_review(tick: Ticket, posts: list, current_user) -> bool:
    # By default, assume we did not write a review for the ticket
    ret_value = False

    # Check whether we already answered the ticket - and then lock
    for my_review in Review.objects.filter(ticket=tick, user=current_user):
        ret_value = True

        # Add our answer to the feed, if it was not already done while adding all answers to our own tickets
        if not tick.user == current_user:
            tmp_dict = {'is_ticket': False,
                        'locked': True,
                        'tick_title': tick.title,
                        'tick_description': tick.description,
                        'tick_time_created': tick.time_created,
                        'tick_image_url': tick.image.url,
                        'rev_time_created': my_review.time_created,
                        'time_created': my_review.time_created,
                        'rev_headline': my_review.headline,
                        'rev_body': my_review.body,
                        'username': my_review.user.username,
                        'rev_answer_to': tick.user.username,
                        'yellow_stars': range(my_review.rating),
                        'empty_stars': range(5 - my_review.rating)
                        }
            posts.append(tmp_dict)

    return ret_value


@login_required
def flux(request):
    current_user = request.user

    # Store all the posts - both tickets and reviews - in a common list of dictionaries sorted by date
    posts = []

    # Find reviews which are answers to the user's tickets
    for my_ticket in Ticket.objects.filter(user=current_user):
        reviews = Review.objects.filter(ticket=my_ticket)
        for rev in reviews:
            tmp_dict = {'is_ticket': False,
                        'locked': True,        # Don't need to edit one of our own tickets from an answer
                        'tick_title': my_ticket.title,
                        'tick_description': my_ticket.description,
                        'tick_time_created': my_ticket.time_created,
                        'tick_image_url': my_ticket.image.url,
                        'rev_time_created': rev.time_created,
                        'time_created': rev.time_created,
                        'rev_headline': rev.headline,
                        'rev_body': rev.body,
                        'username': rev.user.username,
                        'rev_answer_to': current_user.username,
                        'yellow_stars': range(rev.rating),
                        'empty_stars': range(5 - rev.rating),
                        'rev_id': rev.id
                        }
            posts.append(tmp_dict)

    # Then gather all reviews and tickets from the users we are following
    for user_followed in UserFollows.objects.filter(user=current_user):
        tickets = Ticket.objects.filter(user=user_followed.followed_user)
        for tick in tickets:
            tmp_dict = {'is_ticket': True,
                        'locked': check_my_review(tick, posts, current_user),
                        'tick_title': tick.title,
                        'tick_description': tick.description,
                        'tick_time_created': tick.time_created,
                        'time_created': tick.time_created,  # Used to sort the list later
                        'tick_image_url': tick.image.url,
                        'username': tick.user.username,
                        'tick_id': tick.id
                        }
            posts.append(tmp_dict)

        # Same thing for reviews - but we already added answers to our own tickets
        reviews = Review.objects.filter(user=user_followed.followed_user)
        for rev in reviews:
            if not rev.ticket.user == current_user:
                tick = rev.ticket
                tmp_dict = {'is_ticket': False,
                            'locked': check_my_review(tick, posts, current_user),
                            'tick_title': tick.title,
                            'tick_description': tick.description,
                            'tick_time_created': tick.time_created,
                            'tick_image_url': tick.image.url,
                            'rev_time_created': rev.time_created,
                            'time_created': rev.time_created,
                            'rev_headline': rev.headline,
                            'rev_body': rev.body,
                            'username': rev.user.username,
                            'rev_answer_to': tick.user.username,
                            'yellow_stars': range(rev.rating),
                            'empty_stars': range(5 - rev.rating),
                            'rev_id': rev.id,
                            'tick_id': tick.id
                            }
                posts.append(tmp_dict)

    # And finally sort by date
    sorted_posts = sorted(posts, key=lambda x: x['time_created'], reverse=True)

    return render(request, 'blog/flux.html',
                  {'css_name': 'blog/flux.css',
                   'page_title': 'LITReview - Flux',
                   'nav_bar': 'true',
                   'posts': sorted_posts})


@login_required
def follow(request):
    current_user = request.user

    # Message printed if a user can't be followed
    error_msg = ''

    # if this is a POST request we need to process the form data -> add new user to follow
    if request.method == 'POST':
        form = forms.FollowUser(request.POST)
        if form.is_valid():
            # Look for user to follow, if he exists
            try:
                user = User.objects.get(username=form.cleaned_data['username'])
                UserFollows.objects.create(user=current_user, followed_user=user)
            except User.DoesNotExist:
                error_msg = "Erreur: l\'utilisateur n\'a pas été trouvé."

    # Whether it's GET or POST, generate the same page as usual
    form = forms.FollowUser()

    # Extract follow objects which refer to our user, either as a follower or being followed
    followers = []
    following = []
    for obj in UserFollows.objects.all():
        if obj.followed_user.id == current_user.id:
            followers.append(obj.user)
        if obj.user.id == current_user.id:
            following.append(obj)

    return render(request, 'blog/follow.html',
                  {'css_name': 'blog/follow.css',
                   'page_title': 'LITReview - Follow',
                   'nav_bar': 'true',
                   'followers': followers,
                   'following': following,
                   'form_add': form,
                   'error_msg': error_msg})


@login_required
def follow_delete(request, id):
    current_user = request.user
    try:
        obj = UserFollows.objects.get(id=id, user=current_user)
        obj.delete()
    except User.DoesNotExist:
        pass

    return redirect("follow")


@login_required
def my_posts(request):
    current_user = request.user

    # Store our posts - both tickets and reviews - in a common list of dictionaries sorted by date
    posts = []

    # Retrieve tickets and reviews as iterables
    tickets = Ticket.objects.filter(user=current_user)
    reviews = Review.objects.filter(user=current_user)
    tickets = tickets.annotate(content_type=Value('TICKET', CharField()))
    reviews = reviews.annotate(content_type=Value('REVIEW', CharField()))
    posts_obj = sorted(chain(reviews, tickets), key=lambda post: post.time_created, reverse=True)

    # Translate posts into a list of dictionaries for the webpage
    for post in posts_obj:
        if post.content_type == "TICKET":
            tmp_dict = {'is_ticket': True,  # Helpful to sort tickets and reviews later in the webpage
                        'tick_title': post.title,
                        'tick_description': post.description,
                        'tick_time_created': post.time_created,
                        'time_created': post.time_created,          # Field used to sort both reviews and tickets later
                        'tick_image_url': post.image.url,
                        'tick_id': post.id
                        }
        # (If it's not a ticket, it's a REVIEW)
        else:
            tick = post.ticket
            tmp_dict = {'is_ticket': False,     # Not a ticket, but "contains" one of them
                        'tick_title': tick.title,
                        'tick_description': tick.description,
                        'tick_time_created': tick.time_created,
                        'tick_image_url': tick.image.url,
                        'rev_time_created': post.time_created,
                        'time_created': post.time_created,       # This time the review is taken to fill this field
                        'rev_headline': post.headline,
                        'rev_body': post.body,
                        'rev_answer_to': post.ticket.user.username,
                        'yellow_stars': range(post.rating),
                        'empty_stars': range(5 - post.rating),
                        'rev_id': post.id
                        }

        # Fill the list...
        posts.append(tmp_dict)

    return render(request, 'blog/my_posts.html',
                  {'css_name': 'blog/flux.css',
                   'page_title': 'LITReview - My posts',
                   'nav_bar': 'true',
                   'posts': posts})


@login_required
def review(request):
    current_user = request.user

    # POST = add new ticket + review
    if request.method == 'POST' and request.FILES['image']:
        form = forms.ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            # If an error is detected -> go back to posts
            try:
                rating = int(form.cleaned_data['rating'])
                if rating < 0 or rating > 5:
                    return redirect("my_posts")
            except ValueError:
                return redirect("my_posts")

            # Create review and tickets
            tick = Ticket.objects.create(user=current_user,
                                         title=form.cleaned_data['title'],
                                         description=form.cleaned_data['description'],
                                         image=form.cleaned_data['image'])
            Review.objects.create(user=current_user,
                                  ticket=tick,
                                  rating=rating,
                                  headline=form.cleaned_data['headline'],
                                  body=form.cleaned_data['body'])

        # Redirect user to its posts, so he can see the ticket just created
        return redirect("my_posts")

    # GET, nothing particular
    form = forms.ReviewForm()

    return render(request, 'blog/review.html',
                  {'css_name': 'blog/review.css',
                   'page_title': 'LITReview - Review',
                   'nav_bar': 'true',
                   'form_add': form})


@login_required
def review_answer(request, id):
    # Get the review to modify, if it exists + check its owner
    current_user = request.user
    try:
        tick = Ticket.objects.get(id=id)
    except Ticket.DoesNotExist:
        return redirect("flux")

    # POST = modify the ticket
    if request.method == 'POST':
        form = forms.ReviewModifyForm(request.POST)
        if form.is_valid():
            # Catch mistakes in rating if there are
            try:
                rating = int(form.cleaned_data['rating'])
                if rating < 0 or rating > 5:
                    return redirect("flux")
            except ValueError:
                return redirect("flux")

            rating = rating
            Review.objects.create(user=current_user,
                                  ticket=tick,
                                  rating=rating,
                                  headline=form.cleaned_data['headline'],
                                  body=form.cleaned_data['body'])

        # Redirect user to the main feed, so he can see the review he just posted
        return redirect("flux")

    # GET, nothing particular
    form = forms.ReviewModifyForm()

    return render(request, 'blog/review_answer.html',
                  {'css_name': 'blog/review_answer.css',
                   'page_title': 'LITReview - Answer review',
                   'nav_bar': 'true',
                   'form_add': form,
                   'tick_title': tick.title,
                   'tick_description': tick.description,
                   'tick_image_url': tick.image.url,
                   'tick_time_created': tick.time_created,
                   'tick_user': tick.user.username,
                   'tick_id': id})


@login_required
def review_update(request, id):
    # Get the review to modify, if it exists + check its owner
    current_user = request.user
    try:
        rev = Review.objects.get(id=id, user=current_user)
    except Review.DoesNotExist:
        return redirect("my_posts")

    # POST = modify the ticket
    if request.method == 'POST':
        form = forms.ReviewModifyForm(request.POST)
        if form.is_valid():
            rev.headline = form.cleaned_data['headline']
            rev.body = form.cleaned_data['body']

            # Catch mistakes in rating if there are
            try:
                rating = int(form.cleaned_data['rating'])
                if rating < 0 or rating > 5:
                    return redirect("my_posts")
            except ValueError:
                return redirect("my_posts")

            rev.rating = rating
            rev.save()

        # Redirect user to its posts, so he can see the ticket just created
        return redirect("my_posts")

    # GET, nothing particular
    form = forms.ReviewModifyForm()

    return render(request, 'blog/review_modify.html',
                  {'css_name': 'blog/review_modify.css',
                   'page_title': 'LITReview - Update review',
                   'nav_bar': 'true',
                   'form_add': form,
                   'tick_title': rev.ticket.title,
                   'tick_description': rev.ticket.description,
                   'tick_image_url': rev.ticket.image.url,
                   'tick_time_created': rev.ticket.time_created,
                   'tick_user': rev.ticket.user.username,
                   'rev_headline': rev.headline,
                   'rev_body': rev.body,
                   'review_id': id})


@login_required
def review_delete(request, id):
    current_user = request.user
    try:
        obj = Review.objects.get(id=id, user=current_user)
        obj.delete()
    except Ticket.DoesNotExist:
        pass

    return redirect("my_posts")


@login_required
def ticket(request):
    current_user = request.user

    # POST = add new ticket
    if request.method == 'POST' and request.FILES['image']:
        form = forms.TicketForm(request.POST, request.FILES)
        if form.is_valid():
            Ticket.objects.create(user=current_user,
                                  title=form.cleaned_data['title'],
                                  description=form.cleaned_data['description'],
                                  image=form.cleaned_data['image'])
        # Redirect user to its posts, so he can see the ticket just created
        return redirect("my_posts")

    # GET, nothing particular
    form = forms.TicketForm()

    return render(request, 'blog/ticket.html',
                  {'css_name': 'blog/ticket.css',
                   'page_title': 'LITReview - Ticket',
                   'nav_bar': 'true',
                   'form_add': form
                   })


@login_required
def ticket_update(request, id):
    # Get the ticket to modify, if it exists + check its owner
    current_user = request.user
    try:
        tick = Ticket.objects.get(id=id, user=current_user)
    except Ticket.DoesNotExist:
        return redirect("my_posts")

    # POST = modify the ticket
    if request.method == 'POST' and request.FILES['image']:
        form = forms.TicketForm(request.POST, request.FILES)
        if form.is_valid():
            tick.title = form.cleaned_data['title']
            tick.description = form.cleaned_data['description']
            tick.image = form.cleaned_data['image']
            tick.save()
        # Redirect user to its posts, so he can see the ticket just created
        return redirect("my_posts")

    # GET, nothing particular
    form = forms.TicketForm()

    return render(request, 'blog/ticket_modify.html',
                  {'css_name': 'blog/ticket.css',
                   'page_title': 'LITReview - Update ticket',
                   'nav_bar': 'true',
                   'form_add': form,
                   'tick_title': tick.title,
                   'tick_description': tick.description,
                   'tick_image_url': tick.image.url,
                   'ticket_id': id})


@login_required
def ticket_delete(request, id):
    current_user = request.user
    try:
        obj = Ticket.objects.get(id=id, user=current_user)
        obj.delete()
    except Ticket.DoesNotExist:
        pass

    return redirect("my_posts")

