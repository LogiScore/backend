-- Simple Database Structure Export to Markdown
-- Run this in your Supabase SQL Editor

-- First, get table structure
SELECT 
    '```markdown' || E'\n' ||
    '# LogiScore Database Structure' || E'\n' ||
    E'\n' ||
    'Generated on: ' || CURRENT_TIMESTAMP || E'\n' ||
    E'\n' ||
    '## Tables' || E'\n' ||
    E'\n' ||
    '### ' || table_name || E'\n' ||
    E'\n' ||
    '| Column | Type | Nullable | Default |' || E'\n' ||
    '|--------|------|----------|---------|' || E'\n' ||
    string_agg(
        '| ' || column_name || ' | ' || 
        data_type || 
        CASE 
            WHEN character_maximum_length IS NOT NULL THEN '(' || character_maximum_length || ')'
            WHEN numeric_precision IS NOT NULL AND numeric_scale IS NOT NULL THEN '(' || numeric_precision || ',' || numeric_scale || ')'
            WHEN numeric_precision IS NOT NULL THEN '(' || numeric_precision || ')'
            ELSE ''
        END || ' | ' ||
        is_nullable || ' | ' ||
        COALESCE(column_default, 'N/A') || ' |',
        E'\n'
        ORDER BY ordinal_position
    ) || E'\n' ||
    E'\n' ||
    '---' || E'\n' ||
    E'\n' ||
    '```' as markdown_output
FROM information_schema.tables t
JOIN information_schema.columns c ON t.table_name = c.table_name
WHERE t.table_schema = 'public' 
AND t.table_type = 'BASE TABLE'
GROUP BY t.table_name
ORDER BY t.table_name;
