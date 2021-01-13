# Project pages
# Copyright (C) 2020  Nguyễn Gia Phong
# Copyright (C) 2021  Ngô Ngọc Đức Huy
#
# This file is part of Acanban.
#
# Acanban is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Acanban is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Acanban.  If not, see <https://www.gnu.org/licenses/>.

from quart import (Blueprint, ResponseReturnValue, current_app,
                   redirect, render_template, request)
from quart.exceptions import NotFound
from quart_auth import Unauthorized, current_user, login_required
from rethinkdb import r
from rethinkdb.errors import ReqlNonExistenceError

__all__ = ['blueprint']
BASIC_FIELDS = 'id', 'name', 'supervisors', 'students', 'description'

blueprint = Blueprint('project', __name__, url_prefix='/p')


@blueprint.route('/create', methods=['GET', 'POST'])
@login_required
async def create_projects() -> ResponseReturnValue:
    role = await current_user.role
    if role == 'assistant':
        raise Unauthorized
    if request.method == 'GET':
        return await render_template('project-create.html')
    project = await request.form
    project = {'name': project['name'],
               'description': project['description'],
               f'{role}s': [current_user.key]}
    async with current_app.db_pool.connection() as connection:
        response = await r.table('projects').insert(project).run(connection)
        uuid = response['generated_keys'][0]
        await r.table('users').get(current_user.key).update(
            {'projects': r.row['projects'].append(uuid)}).run(connection)
    return redirect(f'/p/{uuid}')


@blueprint.route('/')
async def list_projects() -> ResponseReturnValue:
    """Return a page listing all projects."""
    project_list = r.table('projects').pluck(*BASIC_FIELDS)
    async with current_app.db_pool.connection() as connection:
        projects = await project_list.run(connection)
    return await render_template('project-list.html', projects=projects)


@blueprint.route('/<uuid>/')
@login_required
async def info_redirect(uuid: str) -> ResponseReturnValue:
    """Redirect to the project info page."""
    return redirect(f'/p/{uuid}/info')


@blueprint.route('/<uuid>/info')
@login_required
async def info(uuid: str) -> ResponseReturnValue:
    """Return the page containing the projects' basic infomation."""
    project = r.table('projects').get(uuid)
    async with current_app.db_pool.connection() as connection:
        try:
            project = await project.pluck(*BASIC_FIELDS).run(connection)
        except ReqlNonExistenceError:
            raise NotFound
    try:
        user_projects = await current_user.projects
    except ReqlNonExistenceError:
        raise Unauthorized
    if uuid not in user_projects: raise Unauthorized
    return await render_template('project-info.html', project=project)


@blueprint.route('/<uuid>/edit', methods=['GET', 'POST'])
@login_required
async def edit(uuid: str) -> ResponseReturnValue:
    """Return the page containing the projects' basic infomation."""
    project_query = r.table('projects').get(uuid)
    async with current_app.db_pool.connection() as connection:
        try:
            project = await project_query.pluck(*BASIC_FIELDS).run(connection)
        except ReqlNonExistenceError:
            raise NotFound
        try:
            user_projects = await current_user.projects
        except ReqlNonExistenceError:
            raise Unauthorized
        if uuid not in user_projects: raise Unauthorized
    if request.method == 'GET':
        return await render_template('project-edit.html', project=project)
    updated = {key: value for key, value in (await request.form).items()
               if key in BASIC_FIELDS and value}
    async with current_app.db_pool.connection() as conn:
        await project_query.update(updated).run(conn)
    return redirect(f'/p/{uuid}/info')
