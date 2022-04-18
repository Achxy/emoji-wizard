DELETE FROM guild_prefixes
WHERE guild_id = $1
    AND guild_prefix = $2;