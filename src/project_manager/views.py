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

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import forms
from horizon import exceptions

from openstack_dashboard.dashboards.identity.projects import views as baseViews
from openstack_dashboard import api

from .forms import CourseForm
from .tables import ProjectsTable
from .workflows import ExtUpdateProject
from .workflows import ExtCreateProject

from openstack_auth_shib.models import Project
from openstack_auth_shib.models import PRJ_PRIVATE

from openstack_dashboard.api import keystone as keystone_api

LOG = logging.getLogger(__name__)
baseViews.INDEX_URL = "horizon:idmanager:project_manager:index"

class ExtPrjItem:
    def __init__(self, prj_data):
        self.id = prj_data.id
        self.name = prj_data.name
        self.description = prj_data.description if prj_data.description else ""
        self.enabled = prj_data.enabled
        self.tags = None
        self.status = PRJ_PRIVATE
        self.managed = False

class IndexView(baseViews.IndexView):
    table_class = ProjectsTable
    template_name = 'idmanager/project_manager/index.html'

    def get_data(self):
    
        result = list()
        try:
            tenants = super(IndexView, self).get_data()
            if len(tenants) == 0:
                return result
            
            prj_table = dict()
            for item in tenants:
                prj_table[item.name] = ExtPrjItem(item)

            kprj_man = keystone_api.keystoneclient(self.request).projects

            prj_list = Project.objects.filter(projectname__in=prj_table.keys())
            for prj_item in prj_list:
                prj_table[prj_item.projectname].status = prj_item.status
                prj_table[prj_item.projectname].managed = True

                if prj_item.projectid and self.request.user.is_superuser:
                    prj_table[prj_item.projectname].tags = kprj_man.list_tags(prj_item.projectid)
                else:
                    prj_table[prj_item.projectname].tags = list()
            
            tmplist = prj_table.keys()
            tmplist.sort()
            for item in tmplist:
                result.append(prj_table[item])
            
        except Exception:
            exceptions.handle(self.request, _("Unable to retrieve project list."))
        return result


class UpdateProjectView(baseViews.UpdateProjectView):
    workflow_class = ExtUpdateProject

class CreateProjectView(baseViews.CreateProjectView):
    workflow_class = ExtCreateProject

class ProjectUsageView(baseViews.ProjectUsageView):
    template_name = 'idmanager/project_manager/usage.html'

class DetailProjectView(baseViews.DetailProjectView):
    template_name = 'idmanager/project_manager/detail.html'

    def get_context_data(self, **kwargs):
        context = super(baseViews.DetailProjectView, self).get_context_data(**kwargs)
        project = self.get_data()
        table = ProjectsTable(self.request)
        context["project"] = project
        context["url"] = reverse("horizon:idmanager:project_manager:index")
        context["actions"] = table.render_row_actions(project)
        return context

class CourseView(forms.ModalFormView):
    form_class = CourseForm
    template_name = 'idmanager/project_manager/course.html'
    success_url = reverse_lazy('horizon:idmanager:project_manager:index')

    def get_object(self):
        if not hasattr(self, "_object"):
            self._object = Project.objects.filter(projectid=self.kwargs['project_id'])[0]
        return self._object

    def get_context_data(self, **kwargs):
        context = super(CourseView, self).get_context_data(**kwargs)
        context['projectid'] = self.get_object().projectid
        return context

    def get_initial(self):
        course_info = self.get_object().description.split('|')
        return {
            'projectid' : self.get_object().projectid,
            'description' : course_info[0] if len(course_info) else _('Undefined'),
            'name' : course_info[1] if len(course_info) > 1 else self.get_object().projectname,
            'notes' : course_info[2] if len(course_info) > 2 else ""
        }

