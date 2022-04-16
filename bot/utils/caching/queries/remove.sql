DELETE FROM guild_prefixes
WHERE guild_id = $1
    AND prefix = $2;