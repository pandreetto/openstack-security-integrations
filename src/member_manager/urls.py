#  Copyright (c) 2014 INFN - "Istituto Nazionale di Fisica Nucleare" - Italy
#  All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License. 

from django import VERSION as django_version
from django.conf.urls import url
from openstack_dashboard.dashboards.idmanager.member_manager import views

index_url = url(r'^$', views.IndexView.as_view(), name='index')
modex_url = url(r'^(?P<userid>[^/]+)/modifyexp/$', views.ModifyExpView.as_view(),
                name='modifyexp')

if django_version[1] < 11:

    from django.conf.urls import patterns

    prefix = 'openstack_dashboard.dashboards.idmanager.member_manager.views'

    urlpatterns = patterns(prefix,
        modex_url,
        index_url
    )

else:

    urlpatterns = [
        modex_url,
        index_url
    ]
