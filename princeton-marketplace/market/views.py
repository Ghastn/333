from django.shortcuts import get_object_or_404, render, render_to_response, redirect
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone
from django.http import HttpResponse
from market.models import *
from market.forms import *
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def display_postings(request):
    """
    This view displays either all postings (for a non-authenticated user), or
    postings from subscribed categories, from my posting set, and from my replied set.
    """
    # Get the currently-signed-in user
    user = request.user

    #If the user is authenticated, then display categories
    if user.is_authenticated():
        my_author_list = user.author.all().order_by('date_posted') #List of posts I've authored
        my_respond_list = user.responder.all().order_by('date_posted') #List of posts I've responded to
        full_posting_list = Posting.objects.all().order_by('date_posted') #List of all posts
        posting_list = {} #List of posts in my subscribed categories

        # Build list from subscribed categories
        for category in user.userprofile.categories.all():
            posting_list[category.name] = full_posting_list.filter(category = category)

        context = {'posting_list': posting_list, 'my_author_list': my_author_list, 'my_respond_list': my_respond_list}
        return render(request, 'market/index.html', context)

    # Otherwise, display every post.
    else:
        full_posting_list = Posting.objects.all().order_by('date_posted')
        posting_list = {}

        # Build list from all categories
        for category in Category.objects.all():
            posting_list[category.name] = full_posting_list.filter(category = category)
        context = {'posting_list': posting_list}
        return render(request, 'market/index.html', context)

@login_required
def create_posting(request):
    """
    This view allows an authed user to create a new posting.
    """
    context = RequestContext(request)

    # If we're doing a POST, read in form data and save it
    if request.method == 'POST':
        form = PostingForm(data=request.POST)

        if form.is_valid():
            posting = form.save(commit=False)
            print request.user.username
            posting.author = request.user
            posting.is_open = True
            #posting.responder = None
            posting.date_posted = timezone.now()
            posting.save()
            form.save_m2m()
            return HttpResponseRedirect(reverse('market:index', args=''))
        else:
            print form.errors

    # Otherwise, post the empty form for the user to fill in.
    else:
        form = PostingForm()

    return render_to_response('market/create_posting.html', {'form': form}, context)

def register(request):
    """
    This view allows a new user to create an account.
    """
    context = RequestContext(request)

    # Have we registered yet?
    registered = False

    # If a POST, fill in required user data
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            profile_form.save_m2m()
            registered = True
        
        else:
            print user_form.errors, profile_form.errors

    # Otherwise, send up forms for filling
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render_to_response('market/register.html',
            {'user_form': user_form, 'profile_form': profile_form, 'registered': registered},
            context)

def user_login(request):
    """
    This view allows a user to login.
    """
    context = RequestContext(request)

    # If a POST, fill in required user data and authenticate
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            # Login good, proceed back to home page
            login(request, user)
            return HttpResponseRedirect(reverse('market:index', args=''))
        else:
            # Bad login details were provided. So we can't log the user in.
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")

    # Display the form (note: this form is stuck in the template)
    else:
        return render_to_response('market/login.html', {}, context)

@login_required
def user_logout(request):
    """
    Logs the current user out.
    """
    # Logout the user
    logout(request)

    # Take the user back to the homepage.
    return HttpResponseRedirect(reverse('market:index', args=''))

def posting_detail(request, posting_id):
    """
    This view shows the details of a posting
    """
    posting = get_object_or_404(Posting, pk=posting_id)
    return render(request, 'market/posting_detail.html', {'posting': posting})

@login_required
def user_detail(request, user_id):
    """
    This view shows the details of a user. Only works for signed-in users.
    """
    user = get_object_or_404(User, pk=user_id)
    return render(request, 'market/user_detail.html', {'user': user})