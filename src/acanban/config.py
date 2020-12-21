# Configuration parser
# Copyright (C) 2020  Nguyễn Gia Phong
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

from os.path import isfile, join
from typing import Any, MutableMapping, Sequence

import toml
from appdirs import site_config_dir, user_config_dir
from hypercorn.config import Config as HyperConf

TomMapping = MutableMapping[str, Any]

CONFIG_DIRS = user_config_dir('acanban'), site_config_dir('acanban')
RETHINKDB_DEFAULT: TomMapping = {'db': 'test'}


def hypercorn_config(dirs: Sequence[str] = CONFIG_DIRS) -> HyperConf:
    """Return Hypercorn configuration first found in given directories."""
    for directory in dirs:
        file = join(directory, 'hypercorn.toml')
        if isfile(file): return HyperConf.from_toml(file)
    return HyperConf()


def rethinkdb_config(dirs: Sequence[str] = CONFIG_DIRS) -> TomMapping:
    """Return Hypercorn configuration first found in given directories."""
    for directory in dirs:
        file = join(directory, 'rethinkdb.toml')
        if isfile(file): return toml.load(file)
    return RETHINKDB_DEFAULT