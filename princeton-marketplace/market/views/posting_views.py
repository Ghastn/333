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

######################################################################################
### POSTING MANAGEMENT VIEWS
###     -create_posting(request)
###     -delete_posting(request, posting_id)
###     -close_posting(request, posting_id)
###     -respond_to_posting(request, posting_id)
###     -remove_responder(request, posting_id)
###     -edit_posting(request, posting_id)
###     -posting_detail(request, posting_id)
######################################################################################

@login_required
def create_posting(request):
    """
    This view allows an authed user to create a new posting.
    """

    # If we're doing a POST, read in form data and save it
    if request.method == 'POST':
        form = PostingForm(data=request.POST)

        # Process a valid form:
        if form.is_valid():
            # Save information from the PostingForm
            posting = form.save(commit=False)

            # Save additional information (author, is_open, date_posted)
            posting.author = request.user
            posting.is_open = True
            posting.date_posted = timezone.now()

            # Save the M2M fields (hashtag and category)
            posting.save()
            form.save_m2m()

            # Update the category counts
            posting.category.num_posts = posting.category.num_posts + 1;
            posting.category.save()

            if request.is_ajax():
                return HttpResponse('OK')
            else:
                return HttpResponseRedirect(reverse('market:index', args=''))
        # Return Errors
        else:
            if request.is_ajax():
                errors_dict = {}
                if form.errors:
                    for error in form.errors:
                        e = form.errors[error]
                        errors_dict[error] = unicode(e)
                return HttpResponseBadRequest(json.dumps(errors_dict))
            else:
                print form.errors

    # Otherwise, post the empty form for the user to fill in.
    else:
        form = PostingForm()

    return render(request, 'market/create_posting.html', {'form': form})

@login_required
def delete_posting(request, posting_id):
    """
    This method allows a user to delete a posting (specified by posting_id)
    """
    # Ensure that the posting exists
    try:
        posting = Posting.objects.get(pk=posting_id)
    except Posting.DoesNotExist:
        raise Http404
    else:

        user = request.user
        if request.method == 'POST':
            # Only delete if the currently-logged user authored the post.
            if user == posting.author:
                posting.category.num_posts = posting.category.num_posts - 1;
                posting.category.save()
                posting.delete()
                if request.is_ajax():
                    return HttpReponse('OK')
                else:
                    return HttpResponseRedirect(reverse('market:index', args=''))
            else:
                raise Http404
        # Redirect to homepage
        return HttpResponseRedirect(reverse('market:index', args='')) 

@login_required
def close_posting(request, posting_id):
    """
    Close a posting, updating the transaction count for both the user and the responder
    """
    try:
        posting = Posting.objects.get(pk=posting_id)
    except Posting.DoesNotExist:
        raise Http404
    else:
        user = request.user
        if user != posting.author:
            raise Http404
        if posting.responder is None:
            raise Http404
        if request.method == 'POST':
            user.userprofile.transactions = user.userprofile.transactions + 1
            user.userprofile.save()
            posting.responder.userprofile.transactions = posting.responder.userprofile.transactions + 1
            posting.responder.userprofile.save()
            posting.delete()
            if request.is_ajax():
                return HttpResponse('OK')
            else:
                return HttpResponseRedirect(reverse('market:index', args=''))
        return HttpResponseRedirect(reverse('market:index', args='')) 

@login_required
def respond_to_posting(request, posting_id):
    """
    This method allows a user to respond to a posting (specified by posting_id)
    """

    #Ensure that the posting exists
    try:
        posting = Posting.objects.get(pk=posting_id)
    except Posting.DoesNotExist:
        raise Http404
    else:
        user = request.user
        if request.method == 'POST':

            posting.is_open = False;
            posting.responder = user;
            posting.save()
            posting.category.num_posts = posting.category.num_posts - 1;
            posting.category.save()
            if request.is_ajax():
                return HttpReponse('OK')
            else:
                return HttpResponseRedirect(reverse('market:index', args=''))

        # Redirect to homepage
        return HttpResponseRedirect(reverse('market:index', args='')) 


@login_required
def remove_responder(request, posting_id):
    """
    This method allows a user to respond to a posting (specified by posting_id)
    """

    #Ensure that the posting exists
    try:
        posting = Posting.objects.get(pk=posting_id)
    except Posting.DoesNotExist:
        raise Http404
    else:
        user = request.user
        if request.method == 'POST':
            if request.user == posting.author:
                posting.is_open = True;
                posting.responder = None;
                posting.save()
                posting.category.num_posts = posting.category.num_posts + 1;
                posting.category.save()
                if request.is_ajax():
                    return HttpReponse('OK')
                else:
                    return HttpResponseRedirect(reverse('market:index', args=''))
            else:
                raise Http404
        # Redirect to homepage
        return HttpResponseRedirect(reverse('market:index', args='')) 


@login_required
def edit_posting(request, posting_id):
    """
    """

    try: # validate posting_id
        posting = Posting.objects.get(pk=posting_id)
    except Posting.DoesNotExist:
        raise Http404
    else:
        # If we're doing a POST, read in form data and save it
        if request.method == 'POST': 

            if request.user == posting.author:
                posting_form = PostingEditForm(data=request.POST)


                if posting_form.is_valid():
                    posting.category.num_posts = posting.category.num_posts - 1;
                    posting.category.save()
                    posting_form = PostingEditForm(request.POST, instance=posting)
                    tempposting = posting_form.save(commit=False)
                    tempposting.save()
                    posting_form.save_m2m()
                    tempposting.category.num_posts = posting.category.num_posts + 1;
                    tempposting.category.save()

                    if request.is_ajax():
                        return HttpResponse('OK')
                    else:
                        return HttpResponseRedirect(reverse('market:index', args=''))
                else:
                    if request.is_ajax():
                        errors_dict = {}
                        if posting_form.errors:
                            for error in posting_form.errors:
                                e = posting_form.errors[error]
                                errors_dict[error] = unicode(e)
                        return HttpResponseBadRequest(json.dumps(errors_dict))
                    else:
                        print posting_form.errors
            else:
                raise Http404

        # Otherwise, post the empty form for the user to fill in.
        else:
            if request.user == posting.author:
                posting_form = PostingEditForm(instance=posting)
            else:
                raise Http404

        return render(request, 'market/edit_posting.html',  {'posting_form': posting_form, 'posting_id': posting.id})


def posting_detail(request, posting_id):
    """
    This view gets the details of a posting whose id is posting_id
    """
    try:
        posting = Posting.objects.get(pk=posting_id)
    except Posting.DoesNotExist:
        raise Http404
    else: 
        postdata = {}
        postdata['title'] = posting.title
        postdata['author'] = {"username":posting.author.username, "id":posting.author.id}
        if (posting.responder is not None):
            postdata['responder'] = {"username":posting.responder.username, "id":posting.responder.id}
        else:
            postdata['responder'] = {}
        postdata['date_posted'] = posting.date_posted.__str__()
        postdata['date_expires'] = posting.date_expires.__str__()
        postdata['method_of_payment'] = posting.method_of_pay
        postdata['price'] = posting.price
        postdata['description'] = posting.description
        postdata['selling'] = posting.is_selling
        postdata['open'] = posting.is_open
        postdata['category'] = {"name": posting.category.name, "id": posting.category.id}
        postdata['id'] = posting.id
        postdata['image'] = posting.picture
        hashtags = []
        for hashtag in posting.hashtags.all():
            hashtags.append({"name": hashtag.name, "id": hashtag.id})
        postdata['hashtags'] = hashtags
        return HttpResponse(json.dumps(postdata), content_type="application/json")
