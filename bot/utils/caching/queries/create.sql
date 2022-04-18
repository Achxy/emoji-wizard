/*
EmojiWizard is a project licensed under GNU Affero General Public License.
Copyright (C) 2022-present  Achxy

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
*/

-- Create the prefixes table if it doesn't exist already.
-- Consider not using arrays here because of portability hinderance
-- and 1NF incoompliancy.
-- TODO: Each guild can have 32 or less unique prefixes,
-- Each of such unique prefixes can be up to 32 characters long.

CREATE TABLE IF NOT EXISTS guild_prefixes (
    guild_id BIGINT NOT NULL,
    guild_prefix VARCHAR(32) UNIQUE NOT NULL
);