-- Export Database Relationships to Markdown
-- Run this separately to get all foreign key relationships

SELECT 
    '```markdown' || E'\n' ||
    '# Database Relationships' || E'\n' ||
    E'\n' ||
    'Generated on: ' || CURRENT_TIMESTAMP || E'\n' ||
    E'\n' ||
    '## Foreign Key Relationships' || E'\n' ||
    E'\n' ||
    '| Table | Column | References | Referenced Column | Constraint Name |' || E'\n' ||
    '|-------|--------|------------|-------------------|-----------------|' || E'\n' ||
    string_agg(
        '| ' || tc.table_name || ' | ' || 
        kcu.column_name || ' | ' ||
        ccu.table_name || ' | ' ||
        ccu.column_name || ' | ' ||
        tc.constraint_name || ' |',
        E'\n'
        ORDER BY tc.table_name, kcu.column_name
    ) || E'\n' ||
    E'\n' ||
    '## Relationship Diagram' || E'\n' ||
    E'\n' ||
    string_agg(
        '- **' || tc.table_name || '**.' || kcu.column_name || ' → **' || 
        ccu.table_name || '**.' || ccu.column_name || ' (' || tc.constraint_name || ')',
        E'\n'
        ORDER BY tc.table_name, kcu.column_name
    ) || E'\n' ||
    E'\n' ||
    '## Notes' || E'\n' ||
    E'\n' ||
    '- Foreign keys ensure referential integrity' || E'\n' ||
    '- Relationships are enforced at the database level' || E'\n' ||
    '- Cascade rules can be configured for updates/deletes' || E'\n' ||
    E'\n' ||
    '```' as markdown_output
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage ccu ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
AND tc.table_schema = 'public';
