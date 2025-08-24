-- LogiScore Database Schema Export in Markdown Format
-- Run this in Supabase SQL Editor to get a complete schema overview

WITH table_info AS (
    SELECT 
        t.table_name,
        COUNT(c.column_name) as column_count,
        STRING_AGG(
            '| ' || c.column_name || ' | ' || 
            c.data_type || 
            CASE WHEN c.character_maximum_length IS NOT NULL THEN '(' || c.character_maximum_length || ')' ELSE '' END ||
            CASE WHEN c.numeric_precision IS NOT NULL AND c.numeric_scale IS NOT NULL 
                THEN '(' || c.numeric_precision || ',' || c.numeric_scale || ')' 
                ELSE '' END ||
            CASE WHEN c.is_nullable = 'NO' THEN ' NOT NULL' ELSE '' END ||
            CASE WHEN c.column_default IS NOT NULL THEN ' DEFAULT ' || c.column_default ELSE '' END ||
            ' |',
            E'\n' ORDER BY c.ordinal_position
        ) as columns_md
    FROM information_schema.tables t
    LEFT JOIN information_schema.columns c ON t.table_name = c.table_name
    WHERE t.table_schema = 'public' 
        AND t.table_type = 'BASE TABLE'
        AND t.table_name IN (
            'users', 'user_sessions', 'freight_forwarders', 'branches', 
            'reviews', 'review_questions', 'review_category_scores', 
            'disputes', 'campaigns'
        )
    GROUP BY t.table_name
),
fk_info AS (
    SELECT 
        tc.table_name,
        STRING_AGG(
            '- `' || tc.table_name || '.' || kcu.column_name || '` → `' || 
            ccu.table_name || '.' || ccu.column_name || '`',
            E'\n' ORDER BY kcu.column_name
        ) as foreign_keys_md
    FROM information_schema.table_constraints AS tc
    JOIN information_schema.key_column_usage AS kcu
        ON tc.constraint_name = kcu.constraint_name
    JOIN information_schema.constraint_column_usage AS ccu
        ON ccu.constraint_name = tc.constraint_name
    WHERE tc.constraint_type = 'FOREIGN KEY'
        AND tc.table_schema = 'public'
        AND tc.table_name IN (
            'users', 'user_sessions', 'freight_forwarders', 'branches', 
            'reviews', 'review_questions', 'review_category_scores', 
            'disputes', 'campaigns'
        )
    GROUP BY tc.table_name
),
index_info AS (
    SELECT 
        schemaname,
        tablename,
        STRING_AGG(
            '- `' || indexname || '` (' || indexdef || ')',
            E'\n' ORDER BY indexname
        ) as indexes_md
    FROM pg_indexes
    WHERE schemaname = 'public'
        AND tablename IN (
            'users', 'user_sessions', 'freight_forwarders', 'branches', 
            'reviews', 'review_questions', 'review_category_scores', 
            'disputes', 'campaigns'
        )
    GROUP BY schemaname, tablename
),
stats_info AS (
    SELECT 
        schemaname,
        relname as table_name,
        n_live_tup as live_rows,
        n_dead_tup as dead_rows,
        n_tup_ins as total_inserts,
        n_tup_upd as total_updates,
        n_tup_del as total_deletes
    FROM pg_stat_user_tables
    WHERE schemaname = 'public'
        AND relname IN (
            'users', 'user_sessions', 'freight_forwarders', 'branches', 
            'reviews', 'review_questions', 'review_category_scores', 
            'disputes', 'campaigns'
        )
    )
SELECT 
    '# LogiScore Database Schema Export' || E'\n\n' ||
    'Generated on: ' || NOW() || E'\n\n' ||
    '## Tables Overview' || E'\n\n' ||
    '| Table | Columns | Live Rows | Relationships |' || E'\n' ||
    '|-------|---------|-----------|--------------|' || E'\n' ||
    STRING_AGG(
        '| `' || ti.table_name || '` | ' || ti.column_count || ' | ' || 
        COALESCE(s.live_rows::text, '0') || ' | ' ||
        CASE WHEN fk.foreign_keys_md IS NOT NULL THEN 'Yes' ELSE 'No' END || ' |',
        E'\n' ORDER BY ti.table_name
    ) || E'\n\n' ||
    '## Detailed Schema' || E'\n\n' ||
    STRING_AGG(
        '### `' || ti.table_name || '`' || E'\n\n' ||
        '**Columns:** ' || ti.column_count || E'\n\n' ||
        '| Column | Type |' || E'\n' ||
        '|--------|------|' || E'\n' ||
        ti.columns_md || E'\n' ||
        CASE WHEN fk.foreign_keys_md IS NOT NULL 
            THEN E'\n**Foreign Keys:**\n' || fk.foreign_keys_md || E'\n'
            ELSE ''
        END ||
        CASE WHEN idx.indexes_md IS NOT NULL 
            THEN E'\n**Indexes:**\n' || idx.indexes_md || E'\n'
            ELSE ''
        END ||
        CASE WHEN s.live_rows > 0 
            THEN E'\n**Statistics:** ' || s.live_rows || ' live rows, ' || 
                 COALESCE(s.total_inserts, 0) || ' total inserts' || E'\n'
            ELSE ''
        END ||
        E'\n---\n\n',
        '' ORDER BY ti.table_name
    ) ||
    '## Relationships Summary' || E'\n\n' ||
    '### High Level Relationships' || E'\n' ||
    '- **users** 1 ⟶ ∞ **user_sessions**' || E'\n' ||
    '- **freight_forwarders** 1 ⟶ ∞ **branches**' || E'\n' ||
    '- **users** 1 ⟶ ∞ **reviews**' || E'\n' ||
    '- **branches** 1 ⟶ ∞ **reviews**' || E'\n' ||
    '- **freight_forwarders** 1 ⟶ ∞ **reviews**' || E'\n' ||
    '- **reviews** 1 ⟶ ∞ **review_category_scores**' || E'\n' ||
    '- **review_questions** 1 ⟶ ∞ **review_category_scores** (reference)' || E'\n' ||
    '- **users** 1 ⟶ ∞ **disputes**' || E'\n' ||
    '- **reviews** 1 ⟶ ∞ **disputes**' || E'\n' ||
    '- **freight_forwarders** 1 ⟶ ∞ **disputes**' || E'\n' ||
    '- **users** 1 ⟶ ∞ **disputes (resolved_by)**' || E'\n' ||
    '- **freight_forwarders** 1 ⟶ ∞ **campaigns**' || E'\n\n' ||
    '### Key Notes' || E'\n' ||
    '- A review belongs to both a **branch** and the parent **freight_forwarder**' || E'\n' ||
    '- **review_category_scores** stores individual question ratings (35 questions per review)' || E'\n' ||
    '- **review_questions** serves as a reference table for current question set and rating criteria' || E'\n' ||
    '- Disputes can be filed by a user and optionally resolved by another user' || E'\n' ||
    '- The structure supports detailed analytics on individual question performance' || E'\n\n' ||
    '## Export Information' || E'\n' ||
    '- **Total Tables:** ' || COUNT(*) || E'\n' ||
    '- **Total Columns:** ' || SUM(ti.column_count) || E'\n' ||
    '- **Total Live Rows:** ' || COALESCE(SUM(s.live_rows), 0) || E'\n' ||
    '- **Export Date:** ' || NOW() || E'\n' ||
    '- **Database:** LogiScore Backend v0'
    as markdown_export
FROM table_info ti
LEFT JOIN fk_info fk ON ti.table_name = fk.table_name
LEFT JOIN index_info idx ON ti.table_name = idx.tablename
LEFT JOIN stats_info s ON ti.table_name = s.table_name
GROUP BY ti.table_name, ti.column_count, ti.columns_md, fk.foreign_keys_md, idx.indexes_md, s.live_rows, s.total_inserts;
