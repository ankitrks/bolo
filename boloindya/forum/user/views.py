# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.http import HttpResponsePermanentRedirect
from django.views.decorators.csrf import csrf_exempt

from djconfig import config

from ..core.utils.paginator import yt_paginate
from .utils.email import send_email_change_email
from .utils.tokens import UserEmailChangeTokenGenerator
from ..topic.models import Topic
from ..comment.models import Comment
from .forms import UserProfileForm, EmailChangeForm, UserForm, EmailCheckForm
from django.conf import settings
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from forum.user.models import AppPageContent, ReferralCode, ReferralCodeUsed

User = get_user_model()

@login_required
def update(request):
    # return HttpResponseRedirect('/topic/discussion/')
    if request.method == 'POST':
        uform = UserForm(data=request.POST, instance=request.user)
        form = UserProfileForm(data=request.POST, instance=request.user.st)

        if all([uform.is_valid(), form.is_valid()]):  # TODO: test!
            uform.save()
            form.save()
            messages.info(request, _("Your profile has been updated!"))
            return redirect(reverse('spirit:user:update'))
    else:
        uform = UserForm(instance=request.user)
        form = UserProfileForm(instance=request.user.st)

    context = {
        'form': form,
        'uform': uform
    }

    return render(request, 'spirit/user/profile_update.html', context)


@login_required
def password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)

        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.info(request, _("Your password has been changed!"))
            return redirect(reverse('spirit:user:update'))
    else:
        form = PasswordChangeForm(user=request.user)

    context = {'form': form, }

    return render(request, 'spirit/user/profile_password_change.html', context)


@login_required
def email_change(request):
    if request.method == 'POST':
        form = EmailChangeForm(user=request.user, data=request.POST)

        if form.is_valid():
            send_email_change_email(request, request.user, form.get_email())
            messages.info(request, _("We have sent you an email so you can confirm the change!"))
            return redirect(reverse('spirit:user:update'))
    else:
        form = EmailChangeForm()

    context = {'form': form, }

    return render(request, 'spirit/user/profile_email_change.html', context)


@login_required
def email_change_confirm(request, token):
    user = request.user
    user_email_change = UserEmailChangeTokenGenerator()

    if user_email_change.is_valid(user, token):
        email = user_email_change.get_email()
        form = EmailCheckForm(data={'email': email, })

        if form.is_valid():
            user.email = form.get_email()
            user.save()
            messages.info(request, _("Your email has been changed!"))
            return redirect(reverse('spirit:user:update'))

    messages.error(request, _("Sorry, we were not able to change your email."))
    return redirect(reverse('spirit:user:update'))

@csrf_exempt
def referral_code_validate(request):
    ref_code = request.POST.get('code', '')
    status = 'success'
    message = 'Referral code valid!'
    try:
        code_obj = ReferralCode.objects.exclude(is_active = False).get(code__iexact = ref_code)
    except Exception as e:
        status = 'error'
        message = 'Invalid referral code! Please try again.'
    return JsonResponse({'status' : status, 'message' : message})

@csrf_exempt
def referral_code_update(request):
    ref_code = request.POST.get('code', '')
    user_id = request.POST.get('user_id', '')
    click_id = request.POST.get('click_id','')
    pid = request.POST.get('pid','')
    referral_dump = request.POST.get('referral_dump','')
    android_id = request.POST.get('android_id','')
    status = 'success'
    message = 'Referral code updated!'
    try:
        created = True
        code_obj = ReferralCode.objects.exclude(is_active = False).get(code__iexact = ref_code)
        if user_id: # IF no user_id, means user downloaded the app (not signup)
            used_obj, created = ReferralCodeUsed.objects.get_or_create(code = code_obj, by_user_id = user_id)
        else:
            used_obj = ReferralCodeUsed.objects.create(code = code_obj)
        try:
            used_obj.click_id = click_id
            used_obj.pid =pid
            used_obj.referral_dump = referral_dump
            used_obj.android_id = android_id
            used_obj.save()
        except Exception as e1:
            print e1
            pass
        if not created:
            status = 'error'
            message = 'Referral code already used by user!'
    except Exception as e:
        status = 'error'
        message = 'Invalid referral code! Please try again.'
    return JsonResponse({'status' : status, 'message' : message})

@login_required
def _activity(request, pk, slug, queryset, template, reverse_to, context_name, per_page):
    p_user = get_object_or_404(User, pk=pk)

    if p_user.st.slug != slug:
        url = reverse(reverse_to, kwargs={'pk': p_user.pk, 'slug': p_user.st.slug})
        return HttpResponsePermanentRedirect(url)

    items = yt_paginate(
        queryset,
        per_page=per_page,
        page_number=request.GET.get('page', 1)
    )

    context = {
        'p_user': p_user,
        context_name: items
    }

    return render(request, template, context)


def topics(request, pk, slug):
    user_topics = Topic.objects\
        .visible()\
        .with_bookmarks(user=request.user)\
        .filter(user_id=pk)\
        .order_by('-date', '-pk')\
        .select_related('user__st')

    return _activity(
        request, pk, slug,
        queryset=user_topics,
        template='spirit/user/profile_topics.html',
        reverse_to='spirit:user:topics',
        context_name='topics',
        per_page=settings.TOPICS_PER_PAGE
    )


def comments(request, pk, slug):
    # todo: test with_polls!
    user_comments = Comment.objects\
        .filter(user_id=pk)\
        .visible()\
        .with_polls(user=request.user)

    return _activity(
        request, pk, slug,
        queryset=user_comments,
        template='spirit/user/_user_profile_comments.html',
        reverse_to='spirit:user:detail',
        context_name='comments',
        per_page=settings.COMMENTS_PER_PAGE,
    )


def likes(request, pk, slug):
    # todo: test with_polls!
    user_comments = Comment.objects\
        .filter(comment_likes__user_id=pk)\
        .visible()\
        .with_polls(user=request.user)\
        .order_by('-comment_likes__date', '-pk')

    return _activity(
        request, pk, slug,
        queryset=user_comments,
        template='spirit/user/profile_likes.html',
        reverse_to='spirit:user:likes',
        context_name='comments',
        per_page=settings.COMMENTS_PER_PAGE,
    )


@login_required
def menu(request):
    return render(request, 'spirit/user/menu.html')

@api_view(['GET'])
def getpagecontent(request):
    try:
        name = request.GET.get('name')
        app_page_object = AppPageContent.objects.get(page_name = name)
        print(app_page_object.page_description)
        return JsonResponse({'message' : 'success','description' : app_page_object.page_description})
    except Exception as e:
        return JsonResponse({'message' : 'fail','error':str(e)})
    