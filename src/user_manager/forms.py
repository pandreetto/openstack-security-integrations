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

import logging
from datetime import datetime

from django import http
from django.db import transaction
from django.forms.widgets import HiddenInput
from django.forms.extras.widgets import SelectDateWidget
from django.utils.translation import ugettext as _

from horizon import forms
from horizon import messages

from openstack_auth_shib.models import Registration 
from openstack_auth_shib.models import Expiration
from openstack_auth_shib.models import EMail

from openstack_dashboard.dashboards.identity.users import forms as baseForms

LOG = logging.getLogger(__name__)

class RenewExpForm(forms.SelfHandlingForm):


    def __init__(self, request, *args, **kwargs):

        super(RenewExpForm, self).__init__(request, *args, **kwargs)

        self.fields['userid'] = forms.CharField(
            label=_("User ID"), 
            widget=HiddenInput
        )
        
        curr_year = datetime.now().year
        years_list = range(curr_year, curr_year+25)

        for item in kwargs['initial']:
            if item.startswith('prj_'):
                self.fields[item] = forms.DateTimeField(
                    label="%s %s" % (_("Project"), item[4:]),
                    widget=SelectDateWidget(None, years_list)
                )

    def handle(self, request, data):
        
        with transaction.atomic():
        
            for d_item in data:
                if d_item.startswith('prj_'):
                    q_args = {
                        'registration__userid' : data['userid'],
                        'project__projectname' : d_item[4:]
                    }
                    exp_dates = Expiration.objects.filter(**q_args)
                    exp_dates.update(expdate=data[d_item])
            
        return True

class UpdateUserForm(baseForms.UpdateUserForm):

    def __init__(self, request, *args, **kwargs):
        super(UpdateUserForm, self).__init__(request, *args, **kwargs)
        #
        # TODO email field must be disabled for federated accounts
        #

    def handle(self, request, data):

        user_id = data['id']

        if not "email" in data:
            messages.error(request, _("Email field cannot be empty"))
            return False

        result = True
        try:
            with transaction.atomic():

                tmpres = EMail.objects.filter(registration__userid=user_id)
                tmpres.update(email=data['email'])

                result = super(UpdateUserForm, self).handle(request, data)
                if not result or isinstance(result, http.HttpResponse):
                    raise Exception()

        except:
            # Workaround for calling a roll-back
            LOG.debug("Called roll-back for update user " + user_id, exc_info=True)

        return result


