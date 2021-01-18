# Test project pages
# Copyright (C) 2020-2021  Nguyễn Gia Phong
# Copyright (C) 2020  Ngô Xuân Minh
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

from http import HTTPStatus as Status
from random import choices, uniform
from string import printable
from typing import Optional

from conftest import ClientFactory, parametrize
from pytest import param

# Some members: adaml (student), oliviak (supervisor)
# Some nonmembers: ronanf (supervisor), silasl (assistant)
PROJECT = 'be7a04b8-650f-41dc-912b-10d225baff29'


@parametrize('tab', ('info', 'edit', 'tasks', 'report', 'slides'))
async def test_nonexist(tab: str, user: ClientFactory) -> None:
    """Test accessing tabs on a nonexistent project."""
    adaml = await user('adaml')
    response = await adaml.get(f'/p/this-project-does-not-exist/{tab}')
    assert response.status_code == Status.NOT_FOUND


@parametrize(('username', 'status_code'),
             (param(None, Status.UNAUTHORIZED, id='guest'),
              param('silasl', Status.UNAUTHORIZED, id='assistant'),
              param('ronanf', Status.OK, id='supervisor'),
              param('adaml', Status.OK, id='student')))
async def test_create_get(username: Optional[str], status_code: int,
                          user: ClientFactory) -> None:
    """Test project creation page access permission."""
    client = await user(username)
    response = await client.get('/p/create')
    assert response.status_code == status_code


@parametrize(('username', 'status_code'),
             (param(None, Status.UNAUTHORIZED, id='guest'),
              param('silasl', Status.UNAUTHORIZED, id='assistant'),
              param('ronanf', Status.FOUND, id='supervisor'),
              param('adaml', Status.FOUND, id='student')))
async def test_create_post(username: Optional[str], status_code: int,
                           user: ClientFactory) -> None:
    """Test project creation permission."""
    client = await user(username)
    info = {'name': choices(printable, k=42),
            'description': choices(printable, k=42)}
    response = await client.post('/p/create', form=info)
    assert response.status_code == status_code


@parametrize(('username', 'status_code'),
             (param(None, Status.UNAUTHORIZED, id='guest'),
              param('silasl', Status.UNAUTHORIZED, id='assistant'),
              param('ronanf', Status.UNAUTHORIZED, id='nonmember'),
              param('adaml', Status.OK, id='member')))
@parametrize('tab', ('info', 'edit', 'report'))
async def test_get(username: Optional[str], status_code: int,
                   tab: str, user: ClientFactory) -> None:
    """Test project tabs access permission."""
    client = await user(username)
    response = await client.get(f'/p/{PROJECT}/{tab}')
    assert response.status_code == status_code


async def test_info_redirect(user: ClientFactory) -> None:
    """Test redirect from project's root URI."""
    adaml = await user('adaml')
    response = await adaml.get(f'/p/{PROJECT}/')
    assert response.status_code == Status.FOUND


@parametrize(('username', 'status_code'),
             (param(None, Status.UNAUTHORIZED, id='guest'),
              param('silasl', Status.UNAUTHORIZED, id='assistant'),
              param('ronanf', Status.UNAUTHORIZED, id='nonmember'),
              param('adaml', Status.FOUND, id='member')))
async def test_edit_post(username: Optional[str], status_code: int,
                         user: ClientFactory) -> None:
    """Test project edit permission."""
    client = await user(username)
    info = {'name': choices(printable, k=42),
            'description': choices(printable, k=42)}
    response = await client.post(f'/p/{PROJECT}/edit', form=info)
    assert response.status_code == status_code


@parametrize(('username', 'status_code'),
             (param(None, Status.UNAUTHORIZED, id='guest'),
              param('silasl', Status.UNAUTHORIZED, id='nonstudent nonmember'),
              param('lucyl', Status.UNAUTHORIZED, id='student nonmember'),
              param('oliviak', Status.UNAUTHORIZED, id='nonstudent member'),
              param('adaml', Status.FOUND, id='student member')))
async def test_report_upload(username: Optional[str], status_code: int,
                             user: ClientFactory) -> None:
    """Test POST report file."""
    response = await (await user(username)).post(
        f'/p/{PROJECT}/report/upload',
        headers={
            'Content-Length': 199,
            'Content-Type': (
                'multipart/form-data;'
                ' boundary=------------------------e70696c7f3938bcf')},
        data=(
            b'--------------------------e70696c7f3938bcf\r\n'
            b'Content-Disposition: form-data; name="file"; filename="foo"\r\n'
            b'Content-Type: application/octet-stream\r\n\r\n'
            b'bar\n\r\n--------------------------e70696c7f3938bcf--\r\n'))
    assert response.status_code == status_code


@parametrize(('username', 'status_code'),
             (param(None, Status.UNAUTHORIZED, id='guest'),
              param('silasl', Status.UNAUTHORIZED, id='nonstudent nonmember'),
              param('lucyl', Status.UNAUTHORIZED, id='student nonmember'),
              param('adaml', Status.UNAUTHORIZED, id='student member'),
              param('oliviak', Status.FOUND, id='nonstudent member')))
async def test_report_eval(username: Optional[str], status_code: int,
                           user: ClientFactory) -> None:
    """Test POST report evaluation."""
    client = await user(username)
    evaluation = {'grade': uniform(0, 20), 'comment': choices(printable, k=42)}
    response = await client.post(f'/p/{PROJECT}/report/eval', form=evaluation)
    assert response.status_code == status_code
