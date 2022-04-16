-- Create the prefixes table if it doesn't exist already.
-- Consider not using arrays here because of portability hinderance
-- and 1NF incoompliancy.
-- TODO: Each guild can have 32 or less unique prefixes,
-- Each of such unique prefixes can be up to 32 characters long.

CREATE TABLE IF NOT EXISTS guild_prefixes (
    guild_id BIGINT NOT NULL,
    prefix VARCHAR(32) UNIQUE NOT NULL
);