# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import VideoUploadTranscode,FCMDevice, PushNotificationUser, PushNotification, StateDistrictLanguage, DashboardMetrics, DashboardMetricsJarvis
from functools import update_wrapper
from django.contrib import admin
from django.shortcuts import redirect, render
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _

from fcm.forms import MessageForm
from fcm.utils import get_device_model



admin.site.register(VideoUploadTranscode)

class FCMDeviceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'dev_id', 'reg_id', 'user', 'device_type',)
    # list_filter = ('user__st__name', )
    search_fields = ('user__username', 'user__st__name')
    list_filter = ['is_active']
    # readonly_fields = ('dev_id', 'reg_id', 'created_at')
    actions = ['send_message_action']

    def get_urls(self):
        from django.conf.urls import url

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        urlpatterns = [
            url(r'^send-message/$', wrap(self.send_message_view),
                name=self.build_admin_url('send_message'))]
        return urlpatterns + super(FCMDeviceAdmin, self).get_urls()

    def build_admin_url(self, url_name):
        return '%s_%s_%s' % (self.model._meta.app_label,
                             self.model._meta.model_name,
                             url_name)

    def send_message_view(self, request):
        base_view = 'admin:%s' % self.build_admin_url('changelist')
        session_key = 'device_ids'
        device_ids = request.session.get(session_key)
        if not device_ids:
            return redirect(base_view)

        form = MessageForm(data=request.POST or None)
        if form.is_valid():
            devices = Device.objects.filter(pk__in=device_ids)
            for device in devices:
                device.send_message(form.cleaned_data['message'])
            self.message_user(request, _('Message was sent.'))
            del request.session[session_key]
            return redirect(base_view)

        context = {'form': form, 'opts': self.model._meta, 'add': False}
        return render(request, 'fcm/send_message.html', context)

    def send_message_action(self, request, queryset):
        ids = queryset.values_list('id', flat=True)
        request.session['device_ids'] = list(ids)
        url = 'admin:%s' % self.build_admin_url('send_message')
        return redirect(url)
    send_message_action.short_description = _("Send message")

class StateDistrictLanguageAdmin(admin.ModelAdmin):
    list_display = ('id','state_name','district_name','state_language','district_language')
    search_fields = ('state_name', 'district_name','state_language','district_language')

class DashboardMetricsAdmin(admin.ModelAdmin):
    list_display = ('id', 'metrics', 'metrics_slab', 'date', 'week_no', 'count')
    list_editable = ('metrics', 'metrics_slab', 'date', 'week_no', 'count')
    list_filter = ('metrics', 'metrics_slab', 'date')

class DashboardMetricsJarvisAdmin(admin.ModelAdmin)
    list_display = ('id', 'metrics', 'metrics_slab', 'date', 'week_no', 'count')
    list_editable = ('metrics', 'metrics_slab', 'date', 'week_no', 'count')
    list_filter = ('metrics', 'metrics_slab', 'date')


admin.site.unregister(FCMDevice)
admin.site.register(FCMDevice, FCMDeviceAdmin) 
admin.site.register(PushNotification)
admin.site.register(PushNotificationUser)
admin.site.register(DashboardMetrics, DashboardMetricsAdmin, DashboardMetricsJarvis, DashboardMetricsJarvisAdmin)
admin.site.register(StateDistrictLanguage, StateDistrictLanguageAdmin)
