-- Export Database Structure to Markdown Format
-- Run this in your Supabase SQL Editor to get a complete database documentation

WITH table_info AS (
    SELECT 
        t.table_name,
        t.table_type,
        c.column_name,
        c.data_type,
        c.is_nullable,
        c.column_default,
        c.character_maximum_length,
        c.numeric_precision,
        c.numeric_scale,
        c.ordinal_position
    FROM information_schema.tables t
    LEFT JOIN information_schema.columns c ON t.table_name = c.table_name
    WHERE t.table_schema = 'public'
    AND t.table_type = 'BASE TABLE'
    ORDER BY t.table_name, c.ordinal_position
),
index_info AS (
    SELECT 
        t.table_name,
        i.indexname,
        i.indexdef
    FROM pg_indexes i
    JOIN information_schema.tables t ON i.tablename = t.table_name
    WHERE t.table_schema = 'public'
    AND t.table_type = 'BASE TABLE'
    ORDER BY t.table_name, i.indexname
),
constraint_info AS (
    SELECT 
        tc.table_name,
        tc.constraint_name,
        tc.constraint_type,
        kcu.column_name,
        ccu.table_name AS foreign_table_name,
        ccu.column_name AS foreign_column_name
    FROM information_schema.table_constraints tc
    LEFT JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
    LEFT JOIN information_schema.constraint_column_usage ccu ON ccu.constraint_name = tc.constraint_name
    WHERE tc.table_schema = 'public'
    ORDER BY tc.table_name, tc.constraint_name
)
SELECT 
    '```markdown' || E'\n' ||
    '# LogiScore Database Structure' || E'\n' ||
    E'\n' ||
    'Generated on: ' || CURRENT_TIMESTAMP || E'\n' ||
    E'\n' ||
    '## Database Overview' || E'\n' ||
    E'\n' ||
    'This document describes the complete database structure for the LogiScore application.' || E'\n' ||
    E'\n' ||
    '## Tables' || E'\n' ||
    E'\n' ||
    string_agg(
        '### ' || table_name || E'\n' ||
        E'\n' ||
        '**Table Type:** ' || table_type || E'\n' ||
        E'\n' ||
        '| Column | Type | Nullable | Default | Description |' || E'\n' ||
        '|--------|------|----------|---------|-------------|' || E'\n' ||
        string_agg(
            '| ' || COALESCE(column_name, 'N/A') || ' | ' || 
            COALESCE(data_type, 'N/A') || 
            CASE 
                WHEN character_maximum_length IS NOT NULL THEN '(' || character_maximum_length || ')'
                WHEN numeric_precision IS NOT NULL AND numeric_scale IS NOT NULL THEN '(' || numeric_precision || ',' || numeric_scale || ')'
                WHEN numeric_precision IS NOT NULL THEN '(' || numeric_precision || ')'
                ELSE ''
            END || ' | ' ||
            COALESCE(is_nullable, 'N/A') || ' | ' ||
            COALESCE(column_default, 'N/A') || ' | ' ||
            'Column description' || ' |',
            E'\n'
            ORDER BY ordinal_position
        ) || E'\n' ||
        E'\n',
        E'\n---\n\n'
        ORDER BY table_name
    ) ||
    '## Indexes' || E'\n' ||
    E'\n' ||
    string_agg(
        '### ' || table_name || ' Indexes' || E'\n' ||
        E'\n' ||
        '| Index Name | Definition |' || E'\n' ||
        '|-------------|------------|' || E'\n' ||
        string_agg(
            '| ' || COALESCE(indexname, 'N/A') || ' | ' || 
            COALESCE(indexdef, 'N/A') || ' |',
            E'\n'
            ORDER BY indexname
        ) || E'\n' ||
        E'\n',
        E'\n---\n\n'
        ORDER BY table_name
    ) ||
    '## Constraints' || E'\n' ||
    E'\n' ||
    string_agg(
        '### ' || table_name || ' Constraints' || E'\n' ||
        E'\n' ||
        '| Constraint | Type | Column | Foreign Reference |' || E'\n' ||
        '|------------|------|--------|-------------------|' || E'\n' ||
        string_agg(
            '| ' || COALESCE(constraint_name, 'N/A') || ' | ' || 
            COALESCE(constraint_type, 'N/A') || ' | ' ||
            COALESCE(column_name, 'N/A') || ' | ' ||
            CASE 
                WHEN constraint_type = 'FOREIGN KEY' THEN COALESCE(foreign_table_name || '.' || foreign_column_name, 'N/A')
                ELSE 'N/A'
            END || ' |',
            E'\n'
            ORDER BY constraint_name
        ) || E'\n' ||
        E'\n',
        E'\n---\n\n'
        ORDER BY table_name
    ) ||
    '## Relationships' || E'\n' ||
    E'\n' ||
    'The following relationships exist between tables:' || E'\n' ||
    E'\n' ||
    COALESCE(
        (SELECT string_agg(
            '- **' || table_name || '** → **' || foreign_table_name || '** (via ' || column_name || ' → ' || foreign_column_name || ')',
            E'\n'
            ORDER BY table_name, foreign_table_name
        )
        FROM constraint_info 
        WHERE constraint_type = 'FOREIGN KEY'),
        'No foreign key relationships found.'
    ) || E'\n' ||
    E'\n' ||
    '## Notes' || E'\n' ||
    E'\n' ||
    '- All tables use the `public` schema' || E'\n' ||
    '- Timestamps are in UTC' || E'\n' ||
    '- UUIDs are used for primary keys where applicable' || E'\n' ||
    '- Indexes are created for performance optimization' || E'\n' ||
    E'\n' ||
    '```' as markdown_output
FROM table_info ti
LEFT JOIN index_info ii ON ti.table_name = ii.table_name
LEFT JOIN constraint_info ci ON ti.table_name = ci.table_name
GROUP BY ti.table_name, ti.table_type;
