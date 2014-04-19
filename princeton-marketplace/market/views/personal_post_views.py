from django.shortcuts import get_object_or_404, render, render_to_response, redirect
from django.http import HttpResponseRedirect, HttpResponse, Http404, HttpResponseBadRequest
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone
from django.http import HttpResponse
from market.models import *
from market.forms import *
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import json
from post_helper import return_posts, sort_posts

######################################################################################
### PERSONAL POSTING-BASED VIEWS:
###     -my_open_posts(request)
###     -my_closed_posts(request)
###     -my_responded_posts(request)
######################################################################################

@login_required
def my_open_posts(request, num_items, sorting):
    """
    This view returns JSON data for all postings created by the current user
    that are open. Ordered by date.
    """
    # Get the currently-signed-in user
    user = request.user

    #If the user is authenticated, then display categories
    if user.is_authenticated():
        my_author_list = user.author.all().filter(is_open=True) #List of posts I've authored
        my_author_list = sort_posts(request, sorting, my_author_list)
        # length = 0
        # i = 0
        # try:
        #     i=int(num_items)
        # except ValueError:
        #     i = 0
        # if (i == 0):
        #     length = len(my_author_list)
        # else:
        #     length = i
        # i = 0

        # response_list = []
        # for posting in my_author_list:
        #     postdata = {}
        #     postdata['title'] = posting.title
        #     postdata['author'] = {"username":posting.author.username, "id":posting.author.id}
        #     if (posting.responder is not None):
        #         postdata['responder'] = {"username":posting.responder.username, "id":posting.responder.id}
        #     else:
        #         postdata['responder'] = {}
        #     postdata['date_posted'] = posting.date_posted.__str__()
        #     postdata['date_expires'] = posting.date_expires.__str__()
        #     postdata['method_of_payment'] = posting.method_of_pay
        #     postdata['price'] = posting.price
        #     postdata['description'] = posting.description
        #     postdata['selling'] = posting.is_selling
        #     postdata['open'] = posting.is_open # should all be true
        #     postdata['category'] = {"name": posting.category.name, "id": posting.category.id}
        #     postdata['id'] = posting.id
        #     postdata['image'] = posting.picture
        #     hashtags = []
        #     for hashtag in posting.hashtags.all():
        #         hashtags.append({"name": hashtag.name, "id": hashtag.id})
        #     postdata['hashtags'] = hashtags
        #     response_list.append(postdata)
        #     i=i+1
        #     if (i >= length):
        #         break
        response_list = return_posts(request, num_items, my_author_list)
        return HttpResponse(json.dumps(response_list), content_type="application/json")

@login_required
def my_locked_posts(request, num_items, sorting):
    """
    This view returns JSON data for all postings created by the current user 
    that was responded to. Ordered by date.
    """
    # Get the currently-signed-in user
    user = request.user

    #If the user is authenticated, then display categories
    if user.is_authenticated():
        my_author_list = user.author.all().filter(is_open=False) #List of posts I've authored that have been responded to
        my_author_list = sort_posts(request, sorting, my_author_list)
        # length = 0
        # i = 0
        # try:
        #     i=int(num_items)
        # except ValueError:
        #     i = 0
        # if (i == 0):
        #     length = len(my_author_list)
        # else:
        #     length = i
        # i = 0

        # response_list = []
        # for posting in my_author_list:
        #     postdata = {}
        #     postdata['title'] = posting.title
        #     postdata['author'] = {"username":posting.author.username, "id":posting.author.id}
        #     postdata['responder'] = {"username":posting.responder.username, "id":posting.responder.id}
        #     postdata['date_posted'] = posting.date_posted.__str__()
        #     postdata['date_expires'] = posting.date_expires.__str__()
        #     postdata['method_of_payment'] = posting.method_of_pay
        #     postdata['price'] = posting.price
        #     postdata['description'] = posting.description
        #     postdata['is_selling'] = posting.is_selling
        #     postdata['open'] = posting.is_open # should all be false
        #     postdata['category'] = {"name": posting.category.name, "id": posting.category.id}
        #     postdata['id'] = posting.id
        #     postdata['image'] = posting.picture
        #     hashtags = []
        #     for hashtag in posting.hashtags.all():
        #         hashtags.append({"name": hashtag.name, "id": hashtag.id})
        #     postdata['hashtags'] = hashtags
        #     response_list.append(postdata)
        #     i=i+1
        #     if (i >= length):
        #         break
        response_list = return_posts(request, num_items, my_author_list)
        return HttpResponse(json.dumps(response_list), content_type="application/json")


@login_required
def my_responded_posts(request, num_items, sorting):
    """
    This view returns JSON data for all postings that the logged user 
    has responded to.
    """
    # Get the currently-signed-in user
    user = request.user

    #If the user is authenticated, then display categories
    if user.is_authenticated():
        my_responded_list = user.responder.all().order_by('-date_posted') #List of posts I've responded to
        my_responded_list = sort_posts(request, sorting, my_responded_list)
        # length = 0
        # i = 0
        # try:
        #     i=int(num_items)
        # except ValueError:
        #     i = 0
        # if (i == 0):
        #     length = len(my_responded_list)
        # else:
        #     length = i
        # i = 0

        # response_list = []
        # for posting in my_responded_list:
        #     postdata = {}
        #     postdata['title'] = posting.title
        #     postdata['author'] = {"username":posting.author.username, "id":posting.author.id}
        #     postdata['responder'] = {"username":posting.responder.username, "id":posting.responder.id}
        #     postdata['date_posted'] = posting.date_posted.__str__()
        #     postdata['date_expires'] = posting.date_expires.__str__()
        #     postdata['method_of_payment'] = posting.method_of_pay
        #     postdata['price'] = posting.price
        #     postdata['description'] = posting.description
        #     postdata['is_selling'] = posting.is_selling
        #     postdata['open'] = posting.is_open # should all be false
        #     postdata['category'] = {"name": posting.category.name, "id": posting.category.id}
        #     postdata['id'] = posting.id
        #     postdata['image'] = posting.picture
        #     hashtags = []
        #     for hashtag in posting.hashtags.all():
        #         hashtags.append({"name": hashtag.name, "id": hashtag.id})
        #     postdata['hashtags'] = hashtags
        #     response_list.append(postdata)
        #     i=i+1
        #     if (i >= length):
        #         break
        response_list = return_posts(request, num_items, my_responded_list)
        return HttpResponse(json.dumps(response_list), content_type="application/json")
