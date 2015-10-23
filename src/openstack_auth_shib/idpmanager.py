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
import urllib

from django.conf import settings

from .models import OS_LNAME_LEN


LOG = logging.getLogger(__name__)

def get_manager(request):

    if 'REMOTE_USER' in request.META and request.META.get('AUTH_TYPE','') == 'shibboleth':
        return SAML2_IdP(request)
    
    if 'REMOTE_USER' in request.META and request.path.startswith('/dashboard-google'):
        return Google_IdP(request)
        
    return None



class SAML2_IdP:

    def __init__(self, request):
    
        self.root_url = '/' + request.path.split('/')[1]
        self.logout_prefix = '/Shibboleth.sso/Logout?return=https://%s:%s' % \
            (request.META['SERVER_NAME'], request.META['SERVER_PORT'])
            
        # the remote user corresponds to the ePPN
        self.username = request.META['REMOTE_USER']
        if len(self.username) > OS_LNAME_LEN:
            self.username = self.username[0:OS_LNAME_LEN]
        
        tmpmail = request.META.get('mail', None)
        if tmpmail:
            self.email = tmpmail.split(';')[0]
        else:
            self.email = None
        self.givenname = request.META.get('givenName', None)
        self.sn = request.META.get('sn', None)
        
        # organization as in urn:mace:dir:attribute-def:eduPersonPrincipalName
        idx = request.META['REMOTE_USER'].find('@')
        if idx > 0:
            self.provider = request.META['REMOTE_USER'][idx+1:]
        else:
            self.provider = None
        
    def get_logout_url(self, *args):
        
        result = self.logout_prefix
        if len(args):
            result += args[0]
        else:
            result += '/dashboard'
        return result        
    
    def postproc_logout(self, response):
        return response



class Google_IdP:

    def __init__(self, request):
    
        self.root_url = '/dashboard-google'
        self.logout_prefix = ''
        self.email = request.META.get('HTTP_OIDC_CLAIM_EMAIL', None)
        if self.email:
            self.username = self.email
        else:
            self.username = request.META['REMOTE_USER']
        if len(self.username) > OS_LNAME_LEN:
            self.username = self.username[0:OS_LNAME_LEN]
        self.givenname = request.META.get('HTTP_OIDC_CLAIM_GIVEN_NAME', None)
        self.sn = request.META.get('HTTP_OIDC_CLAIM_FAMILY_NAME', None)
        self.provider = 'Google'

    def get_logout_url(self, *args):
        
        if len(args):
            return args[0]
        return '/dashboard'
    
    def postproc_logout(self, response):
        #
        # TODO verify logout
        #
        response.delete_cookie('mod_auth_openidc_session')
        return response




def get_idp_list(excl_list=list()):

    result = list()
    
    idp_list = settings.HORIZON_CONFIG.get('identity_providers', [])

    for idp_data in idp_list:
        #
        # TODO check if item is well-formed, see _login.html
        # Accepted keys:
        # id: IdP id (infn.it, unipd.it, etc)
        # path: URL path prefix (/dashboard-shib, /dashboard-google, etc.)
        # description: IdP short description
        # logo: URL path for the logo (/static/dashboard/img/logoInfnAAI.png)
        #
        if not idp_data['id'] in excl_list:
            resume_url = '%s/project/idp_requests/resume/' % idp_data['path']
            idp_data['resume_query'] = urllib.urlencode({'url' : resume_url})
            result.append(idp_data)

    return result









