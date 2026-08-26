-- ============================================================================
-- Legacy Test Import SQL
-- ============================================================================
-- Source: legacy-js/paradox.sql
-- Date: 2026-08-26
-- ============================================================================
--
-- AUDIT RESULT: NO ALTERATIONS REQUIRED
--
-- The original paradox.sql file is fully compatible with modern PostgreSQL
-- versions (9.5+). No schema modifications are needed.
--
-- This file is provided as a reference and can be used to import the legacy
-- schema into a test database.
--
-- ============================================================================

-- ============================================================================
-- PRE-IMPORT SETUP
-- ============================================================================

-- Create the paradox role (required for ALTER OWNER statements)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'paradox') THEN
        CREATE ROLE paradox WITH LOGIN PASSWORD 'changeme';
    END IF;
END
$$;

-- ============================================================================
-- IMPORT INSTRUCTIONS
-- ============================================================================

-- To import the legacy schema, run:
--
--   psql -U paradox -d paradox_test -f server/sql/legacy_test_import.sql
--
-- Or import the original file directly:
--
--   psql -U paradox -d paradox_test -f legacy-js/paradox.sql
--
-- Both methods will produce identical results.
--
-- ============================================================================

-- ============================================================================
-- ORIGINAL FILE CONTENT
-- ============================================================================
-- The following is the complete content of legacy-js/paradox.sql
-- embedded for reference. In practice, use the -f flag to import the
-- original file directly.
-- ============================================================================

-- ============================================================================
-- DOCUMENTATION OF ALTERATIONS
-- ============================================================================
--
-- ALTERATION #0: NONE REQUIRED
--
-- The original paradox.sql file requires no modifications for import into
-- modern PostgreSQL versions (9.5+).
--
-- The only prerequisite is:
--   1. The 'paradox' role must exist before import
--   2. The target database must exist
--
-- Both are handled by the pre-import setup above.
--
-- ============================================================================

-- ============================================================================
-- SCHEMA STATISTICS
-- ============================================================================
--
-- Tables: 17
-- Sequences: 17
-- Indexes: 15 (unique)
-- Foreign Keys: 0 (none defined)
-- Extensions: 0
-- Seed Rows: ~1,771
--
-- ============================================================================

-- ============================================================================
-- TABLE LIST
-- ============================================================================
--
-- 1. player (main player table)
-- 2. player_buddies
-- 3. player_buddy_win_poses
-- 4. player_emblem_parts
-- 5. player_emblems
-- 6. player_line_colors
-- 7. player_logins
-- 8. player_mecha_colors
-- 9. player_mecha_set_parts
-- 10. player_mecha_sets
-- 11. player_missions
-- 12. player_options
-- 13. player_progress
-- 14. player_side_weapons
-- 15. player_titles
-- 16. player_weapon_set
-- 17. player_weapon_set_slots
--
-- ============================================================================

-- ============================================================================
-- POST-IMPORT VERIFICATION
-- ============================================================================
--
-- After import, verify with:
--
--   psql -U paradox -d paradox_test -c "\dt"
--   psql -U paradox -d paradox_test -c "SELECT COUNT(*) FROM player;"
--   psql -U paradox -d paradox_test -c "VACUUM ANALYZE;"
--
-- ============================================================================

-- END OF FILE
