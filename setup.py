#!/usr/bin/env python

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

import sys, os, os.path, shlex, subprocess
from subprocess import Popen as execScript
from distutils.core import setup
from distutils.command.bdist_rpm import bdist_rpm as _bdist_rpm

pkg_name = 'openstack-security-integrations'
pkg_version = '1.0.6'
pkg_release = '1'

source_items = "setup.py src config"

class bdist_rpm(_bdist_rpm):

    def run(self):

        topdir = os.path.join(os.getcwd(), self.bdist_base, 'rpmbuild')
        builddir = os.path.join(topdir, 'BUILD')
        srcdir = os.path.join(topdir, 'SOURCES')
        specdir = os.path.join(topdir, 'SPECS')
        rpmdir = os.path.join(topdir, 'RPMS')
        srpmdir = os.path.join(topdir, 'SRPMS')
        
        cmdline = "mkdir -p %s %s %s %s %s" % (builddir, srcdir, specdir, rpmdir, srpmdir)
        execScript(shlex.split(cmdline)).communicate()
        
        cmdline = "tar -zcf %s %s" % (os.path.join(srcdir, pkg_name + '.tar.gz'), source_items)
        execScript(shlex.split(cmdline)).communicate()
        
        specOut = open(os.path.join(specdir, pkg_name + '.spec'),'w')
        cmdline = "sed -e 's|@PKGVERSION@|%s|g' -e 's|@PKGRELEASE@|%s|g' project/%s.spec.in" % (pkg_version, pkg_release, pkg_name)
        execScript(shlex.split(cmdline), stdout=specOut, stderr=sys.stderr).communicate()
        specOut.close()
        
        cmdline = "rpmbuild -ba --define '_topdir %s' %s.spec" % (topdir, os.path.join(specdir, pkg_name))
        execScript(shlex.split(cmdline)).communicate()

os_main_dir = 'usr/share/openstack-dashboard/'
templates_dir = os_main_dir + 'openstack_dashboard/templates'
img_dir = os_main_dir + 'static/dashboard/img'
reg_panel_dir = os_main_dir + 'openstack_dashboard/dashboards/admin/registration_manager/templates/registration_manager'
subscr_panel_dir = os_main_dir + 'openstack_dashboard/dashboards/project/subscription_manager/templates/subscription_manager'
member_panel_dir = os_main_dir + 'openstack_dashboard/dashboards/project/member_manager/templates/member_manager'
user_panel_dir = os_main_dir + 'openstack_dashboard/dashboards/admin/user_manager/templates/user_manager'
pwd_panel_dir = os_main_dir + 'openstack_dashboard/dashboards/settings/password_manager/templates/password_manager'
preq_panel_dir = os_main_dir + 'openstack_dashboard/dashboards/project/project_requests/templates/project_requests'
idpreq_panel_dir = os_main_dir + 'openstack_dashboard/dashboards/project/idp_requests/templates/idp_requests'
css_dir = 'usr/share/openstack-dashboard/static/dashboard/less'

template_list = [
    'src/templates/_register_form.html',
    'src/templates/registration.html',
    'src/templates/aai_error.html',
    'src/templates/aai_registration_ok.html'
]

reg_templ_list = [
    'src/templates/registration_manager/reg_process.html',
    'src/templates/registration_manager/_reg_process.html',
    'src/templates/registration_manager/reg_manager.html',
    'src/templates/registration_manager/reg_approve.html',
    'src/templates/registration_manager/_reg_approve.html'
]

subscr_templ_list = [
    'src/templates/subscription_manager/subscr_manager.html',
    'src/templates/subscription_manager/subscr_approve.html',
    'src/templates/subscription_manager/_subscr_approve.html'
]

member_templ_list = [
    'src/templates/member_manager/member_manager.html'
]

usr_templ_list = [
    'src/templates/user_manager/index.html',
    'src/templates/user_manager/renewexp.html',
    'src/templates/user_manager/_renewexp.html',
    'src/templates/user_manager/update.html',
    'src/templates/user_manager/_update.html'
]

pwd_templ_list = [
    'src/templates/password_manager/activate.html',
    'src/templates/password_manager/_activate.html'
]

preq_templ_list = [
    'src/templates/project_requests/prj_request.html',
    'src/templates/project_requests/_prj_request.html'
]

idpreq_templ_list = [
    'src/templates/idp_requests/idp_request.html',
    'src/templates/idp_requests/_idp_request.html'
]

logo_list = [
    'src/templates/logoCloudAreapd.png',
    'src/templates/logoCloudAreapdStrip.png',
    'src/templates/logoInfnAAI.png',
    'src/templates/logoGoogle.png',
    'src/templates/logoUsrPwd.png',
    'src/templates/logoIDEM.png',
    'src/templates/logoCloudAreapd.ico'
]

module_list = [
    'keystone_skey_auth',
    'openstack_auth_shib',
    'registration_manager',
    'project_manager',
    'subscription_manager',
    'member_manager',
    'user_manager',
    'password_manager',
    'project_requests',
    'idp_requests',
    'commands'
]

confile_list = [
    'config/attribute-map.xml',
    'config/idem-template-metadata.xml',
    'config/logging.conf',
    'config/actions.conf'
]

setup(
      name=pkg_name,
      version=pkg_version,
      description='Shibboleth-Openstack integrations',
      long_description='''Shibboleth-Openstack integrations''',
      license='Apache Software License',
      author_email='CREAM group <cream-support@lists.infn.it>',
      packages=module_list,
      package_dir = {'': 'src'},
      data_files=[
                  (templates_dir, template_list),
                  (templates_dir + '/auth', ['src/templates/_login.html']),
                  (reg_panel_dir, reg_templ_list),
                  (user_panel_dir, usr_templ_list),
                  (pwd_panel_dir, pwd_templ_list),
                  (subscr_panel_dir, subscr_templ_list),
                  (member_panel_dir, member_templ_list),
                  (preq_panel_dir, preq_templ_list),
                  (idpreq_panel_dir, idpreq_templ_list),
                  (css_dir, ['src/templates/aai_infn_integrations.less']),
                  (img_dir, logo_list),
                  ('etc/openstack-auth-shib', confile_list),
                  ('etc/keystone-skey-auth', ['config/policy.json']),
                  ('etc/cron.d', ['config/openstack-auth-shib-cron']),
                  ('usr/share/openstack-auth-shib', ['config/attribute-map.xml']),
                  ('usr/share/openstack-auth-shib/templates', ['config/notifications_en.txt'])
                 ],
      cmdclass={'bdist_rpm': bdist_rpm}
     )


