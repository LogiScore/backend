-- Complete Database Structure Export with Relationships
-- Run this in your Supabase SQL Editor to get everything in one go

WITH table_structure AS (
    SELECT 
        t.table_name,
        string_agg(
            '| ' || c.column_name || ' | ' || 
            c.data_type || 
            CASE 
                WHEN c.character_maximum_length IS NOT NULL THEN '(' || c.character_maximum_length || ')'
                WHEN c.numeric_precision IS NOT NULL AND c.numeric_scale IS NOT NULL THEN '(' || c.numeric_precision || ',' || c.numeric_scale || ')'
                WHEN c.numeric_precision IS NOT NULL THEN '(' || c.numeric_precision || ')'
                ELSE ''
            END || ' | ' ||
            c.is_nullable || ' | ' ||
            COALESCE(c.column_default, 'N/A') || ' |',
            E'\n'
            ORDER BY c.ordinal_position
        ) as columns_md
    FROM information_schema.tables t
    JOIN information_schema.columns c ON t.table_name = c.table_name
    WHERE t.table_schema = 'public' 
    AND t.table_type = 'BASE TABLE'
    GROUP BY t.table_name
),
table_indexes AS (
    SELECT 
        t.table_name,
        string_agg(
            '| ' || i.indexname || ' | ' || i.indexdef || ' |',
            E'\n'
            ORDER BY i.indexname
        ) as indexes_md
    FROM information_schema.tables t
    LEFT JOIN pg_indexes i ON i.tablename = t.table_name
    WHERE t.table_schema = 'public' 
    AND t.table_type = 'BASE TABLE'
    GROUP BY t.table_name
),
relationships AS (
    SELECT 
        string_agg(
            '| ' || tc.table_name || ' | ' || 
            kcu.column_name || ' | ' ||
            ccu.table_name || ' | ' ||
            ccu.column_name || ' | ' ||
            tc.constraint_name || ' |',
            E'\n'
            ORDER BY tc.table_name, kcu.column_name
        ) as relationships_table,
        string_agg(
            '- **' || tc.table_name || '**.' || kcu.column_name || ' → **' || 
            ccu.table_name || '**.' || ccu.column_name || ' (' || tc.constraint_name || ')',
            E'\n'
            ORDER BY tc.table_name, kcu.column_name
        ) as relationships_list
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
    JOIN information_schema.constraint_column_usage ccu ON ccu.constraint_name = tc.constraint_name
    WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_schema = 'public'
),
complete_output AS (
    SELECT 
        string_agg(
            '### ' || ts.table_name || E'\n' ||
            E'\n' ||
            '| Column | Type | Nullable | Default |' || E'\n' ||
            '|--------|------|----------|---------|' || E'\n' ||
            ts.columns_md || E'\n' ||
            E'\n' ||
            '**Indexes:**' || E'\n' ||
            E'\n' ||
            '| Index Name | Definition |' || E'\n' ||
            '|-------------|------------|' || E'\n' ||
            COALESCE(ti.indexes_md, '| No indexes found | |') || E'\n' ||
            E'\n' ||
            '---' || E'\n' ||
            E'\n',
            E'\n'
            ORDER BY ts.table_name
        ) as tables_md
    FROM table_structure ts
    LEFT JOIN table_indexes ti ON ts.table_name = ti.table_name
)
SELECT 
    '```markdown' || E'\n' ||
    '# LogiScore Complete Database Structure' || E'\n' ||
    E'\n' ||
    'Generated on: ' || CURRENT_TIMESTAMP || E'\n' ||
    E'\n' ||
    '## Database Overview' || E'\n' ||
    E'\n' ||
    'This document describes the complete database structure including tables, columns, indexes, and relationships.' || E'\n' ||
    E'\n' ||
    '## Tables' || E'\n' ||
    E'\n' ||
    co.tables_md ||
    '## Database Relationships' || E'\n' ||
    E'\n' ||
    '### Foreign Key Relationships' || E'\n' ||
    E'\n' ||
    '| Table | Column | References | Referenced Column | Constraint Name |' || E'\n' ||
    '|-------|--------|------------|-------------------|-----------------|' || E'\n' ||
    COALESCE(r.relationships_table, '| No foreign key relationships found | | | | |') || E'\n' ||
    E'\n' ||
    '### Relationship Diagram' || E'\n' ||
    E'\n' ||
    COALESCE(r.relationships_list, 'No foreign key relationships found.') || E'\n' ||
    E'\n' ||
    '## Summary' || E'\n' ||
    E'\n' ||
    '- **Total Tables:** ' || (SELECT COUNT(*) FROM table_structure) || E'\n' ||
    '- **Total Relationships:** ' || COALESCE((SELECT COUNT(*) FROM information_schema.table_constraints WHERE constraint_type = 'FOREIGN KEY' AND table_schema = 'public'), 0) || E'\n' ||
    '- **Schema:** public' || E'\n' ||
    '- **Generated:** ' || CURRENT_TIMESTAMP || E'\n' ||
    E'\n' ||
    '## Notes' || E'\n' ||
    E'\n' ||
    '- All tables use the `public` schema' || E'\n' ||
    '- Timestamps are in UTC' || E'\n' ||
    '- Indexes are created for performance optimization' || E'\n' ||
    '- Foreign keys ensure referential integrity' || E'\n' ||
    E'\n' ||
    '```' as complete_markdown
FROM complete_output co
CROSS JOIN relationships r;
