# Legacy SQL Import Audit

## Date: 2026-08-26

## Source File: `legacy-js/paradox.sql`

---

## 1. Required PostgreSQL Version

**Original Version:** PostgreSQL 12.6 (Ubuntu 12.6-0ubuntu0.20.04.1)

**Minimum Compatible Version:** PostgreSQL 9.4+ (uses `ON CONFLICT` syntax introduced in 9.5)

**Recommended Version:** PostgreSQL 14.x or 15.x (as per `WINDOWS_POSTGRESQL_SETUP.md`)

**Version-Specific Syntax:**
- No version-specific syntax detected
- All SQL is compatible with PostgreSQL 9.5+
- Uses standard `CREATE TABLE`, `ALTER TABLE`, `COPY`, and `CREATE INDEX` statements

---

## 2. Database Owner Assumptions

**Owner:** `paradox`

All tables, sequences, and indexes are owned by the `paradox` role.

**Impact:** The `paradox` role must exist before importing the schema.

**Required Setup:**
```sql
CREATE ROLE paradox WITH LOGIN PASSWORD 'changeme';
```

---

## 3. Role Assumptions

**Required Roles:**
- `paradox` - Database owner (required for all objects)

**No other roles are assumed or created.**

---

## 4. CREATE DATABASE Statements

**None found.**

The SQL dump assumes it will be imported into an existing database.

**Required Setup:**
```sql
CREATE DATABASE paradox OWNER paradox;
```

---

## 5. ALTER OWNER Statements

**16 ALTER OWNER statements found:**

All tables and sequences are owned by `paradox`:

| Object Type | Object Name | Owner |
|-------------|-------------|-------|
| TABLE | player_buddy_win_poses | paradox |
| SEQUENCE | buddy_win_poses_id_seq | paradox |
| TABLE | player_mecha_colors | paradox |
| SEQUENCE | mecha_colors_id_seq | paradox |
| TABLE | player | paradox |
| TABLE | player_buddies | paradox |
| SEQUENCE | player_buddies_id_seq | paradox |
| TABLE | player_emblem_parts | paradox |
| SEQUENCE | player_emblem_parts_id_seq | paradox |
| TABLE | player_emblems | paradox |
| SEQUENCE | player_emblems_id_seq | paradox |
| TABLE | player_line_colors | paradox |
| SEQUENCE | player_line_colors_id_seq | paradox |
| TABLE | player_logins | paradox |
| SEQUENCE | player_logins_id_seq | paradox |
| TABLE | player_mecha_set_parts | paradox |
| SEQUENCE | player_mecha_set_parts_id_seq | paradox |
| TABLE | player_mecha_sets | paradox |
| SEQUENCE | player_mecha_sets_id_seq | paradox |
| TABLE | player_missions | paradox |
| SEQUENCE | player_missions_id_seq | paradox |
| TABLE | player_options | paradox |
| SEQUENCE | player_options_id_seq | paradox |
| TABLE | player_progress | paradox |
| SEQUENCE | player_progress_id_seq | paradox |
| TABLE | player_side_weapons | paradox |
| SEQUENCE | player_side_weapons_id_seq | paradox |
| TABLE | player_titles | paradox |
| SEQUENCE | player_titles_id_seq | paradox |
| TABLE | player_weapon_set | paradox |
| TABLE | player_weapon_set_slots | paradox |
| SEQUENCE | player_weapon_set_slots_id_seq | paradox |
| SEQUENCE | weapon_set_id_seq | paradox |

---

## 6. Extensions Used

**None found.**

No `CREATE EXTENSION` statements are present.

---

## 7. Sequences Defined

**16 sequences defined:**

| Sequence Name | Table | Column | Start | Increment |
|---------------|-------|--------|-------|-----------|
| buddy_win_poses_id_seq | player_buddy_win_poses | id | 1 | 1 |
| mecha_colors_id_seq | player_mecha_colors | id | 1 | 1 |
| player_buddies_id_seq | player_buddies | id | 1 | 1 |
| player_emblem_parts_id_seq | player_emblem_parts | id | 1 | 1 |
| player_emblems_id_seq | player_emblems | id | 1 | 1 |
| player_line_colors_id_seq | player_line_colors | id | 1 | 1 |
| player_logins_id_seq | player_logins | id | 1 | 1 |
| player_mecha_set_parts_id_seq | player_mecha_set_parts | id | 1 | 1 |
| player_mecha_sets_id_seq | player_mecha_sets | id | 1 | 1 |
| player_missions_id_seq | player_missions | id | 1 | 1 |
| player_options_id_seq | player_options | id | 1 | 1 |
| player_player_id_seq | player | player_id | 1 | 1 |
| player_progress_id_seq | player_progress | id | 1 | 1 |
| player_side_weapons_id_seq | player_side_weapons | id | 1 | 1 |
| player_titles_id_seq | player_titles | id | 1 | 1 |
| player_weapon_set_slots_id_seq | player_weapon_set_slots | id | 1 | 1 |
| weapon_set_id_seq | player_weapon_set | id | 1 | 1 |

**Sequence Values Set:**

| Sequence | Current Value |
|----------|---------------|
| buddy_win_poses_id_seq | 14 |
| mecha_colors_id_seq | 84 |
| player_buddies_id_seq | 15456 |
| player_emblem_parts_id_seq | 60 |
| player_emblems_id_seq | 24 |
| player_line_colors_id_seq | 15 |
| player_logins_id_seq | 166 |
| player_mecha_set_parts_id_seq | 700 |
| player_mecha_sets_id_seq | 140 |
| player_missions_id_seq | 2629 |
| player_options_id_seq | 466 |
| player_player_id_seq | 10011 |
| player_progress_id_seq | 4907 |
| player_side_weapons_id_seq | 36 |
| player_titles_id_seq | 26 |
| player_weapon_set_slots_id_seq | 728 |
| weapon_set_id_seq | 224 |

---

## 8. Foreign Keys

**None defined.**

The schema has no foreign key constraints. All relationships are implicit through `player_id` columns.

---

## 9. Missing Foreign Keys

**Tables that should reference `player.player_id`:**

| Table | Column | Should Reference |
|-------|--------|------------------|
| player_buddies | player_id | player.player_id |
| player_buddy_win_poses | player_id | player.player_id |
| player_emblem_parts | player_id | player.player_id |
| player_emblems | player_id | player.player_id |
| player_line_colors | player_id | player.player_id |
| player_logins | player_id | player.player_id |
| player_mecha_colors | player_id | player.player_id |
| player_mecha_set_parts | player_id | player.player_id |
| player_mecha_sets | player_id | player.player_id |
| player_missions | player_id | player.player_id |
| player_options | player_id | player.player_id |
| player_progress | player_id | player.player_id |
| player_side_weapons | player_id | player.player_id |
| player_titles | player_id | player.player_id |
| player_weapon_set | player_id | player.player_id |
| player_weapon_set_slots | player_id | player.player_id |

**Note:** Foreign keys are intentionally omitted in the legacy schema. This is common in game databases for performance reasons.

---

## 10. Indexes

**15 unique indexes defined:**

| Index Name | Table | Columns |
|------------|-------|---------|
| buddy_win_poses_player_id_buddy_id_win_pose_id_key | player_buddy_win_poses | player_id, buddy_id, win_pose_id |
| mecha_colors_player_id_mecha_color_id_key | player_mecha_colors | player_id, mecha_color_id |
| player_buddies_player_id_buddy_id_buddy_option_key | player_buddies | player_id, buddy_id, buddy_key |
| player_emblem_parts_player_id_part_id_key | player_emblem_parts | player_id, part_id |
| player_line_colors_player_id_side_line_color_id_key | player_line_colors | player_id, line_color_id |
| player_mecha_set_parts_player_id_mecha_set_id_part_id_key | player_mecha_set_parts | player_id, mecha_set_id, part_id |
| player_mecha_sets_player_id_mecha_set_id_key | player_mecha_sets | player_id, mecha_set_id |
| player_missions_player_id_mission_id_key | player_missions | player_id, mission_id |
| player_options_player_id_option_key | player_options | player_id, option_key |
| player_progress_player_id_progress_key | player_progress | player_id, progress_key |
| player_side_weapons_player_id_side_weapon_id_key | player_side_weapons | player_id, side_weapon_id |
| player_titles_player_id_emblem_id_key | player_emblems | player_id, emblem_id |
| player_titles_player_id_title_id_key | player_titles | player_id, title_id |
| player_weapon_set_slots_player_id_weapon_set_key | player_weapon_set_slots | player_id, weapon_set_id, slot_id |
| weapon_set_player_id_weapon_set_key | player_weapon_set | player_id, weapon_set_id |

---

## 11. Default Values

**Columns with DEFAULT values:**

| Table | Column | Default |
|-------|--------|---------|
| player_buddy_win_poses | status | 0 |
| player_mecha_colors | status | 0 |
| player | player_name | 'ＮｏＮａｍｅ' |
| player | rank_id | 0 |
| player | rank_id_2on2 | 0 |
| player | title_id | 0 |
| player | title_id_2on2 | 0 |
| player | buddy_id | 0 |
| player | buddy_intimacy | 0 |
| player | line_color_id | 0 |
| player | ranking_pref_name | '東京' |
| player | last_ranking_pref_name | '東京' |
| player | match_mode_id | 0 |
| player | violation_point | 0 |
| player | emblem_id | 0 |
| player | line_color_id_2on2 | 0 |
| player | emblem_id_2on2 | 0 |
| player | birth_day | 1 |
| player | birth_month | 1 |
| player | mecha_set_id | 0 |
| player | side_weapon_id | 0 |
| player | mecha_preset_id | 0 |
| player | rank_point | 0 |
| player | max_rank_id | 0 |
| player | rank_point_2on2 | 0 |
| player | max_rank_id_2on2 | 0 |
| player_buddies | buddy_value | 0 |
| player_emblem_parts | status | 0 |
| player_emblems | status | 0 |
| player_emblems | editable | false |
| player_line_colors | status | 0 |
| player_logins | location_id | 0 |
| player_logins | client_version | 0 |
| player_logins | data_version | 0 |
| player_mecha_set_parts | design_id | 0 |
| player_mecha_set_parts | color_id | 0 |
| player_mecha_sets | is_decal | false |
| player_mecha_sets | favorite | false |
| player_mecha_sets | use_count | 0 |
| player_mecha_sets | use_time | 0 |
| player_mecha_sets | status | 0 |
| player_mecha_sets | win_count | 0 |
| player_mecha_sets | winning_streaks | 0 |
| player_missions | clear_count | 0 |
| player_missions | clear_num | 0 |
| player_missions | status | 0 |
| player_missions | mission_status | 0 |
| player_options | value_num | 0 |
| player_progress | status | 0 |
| player_side_weapons | use_count | 0 |
| player_side_weapons | use_time | 0 |
| player_side_weapons | status | 0 |
| player_titles | status | 0 |
| player_weapon_set | use_count | 0 |
| player_weapon_set | use_time | 0 |
| player_weapon_set | status | 0 |
| player_weapon_set_slots | use_count | 0 |
| player_weapon_set_slots | use_time | 0 |

---

## 12. Encoding

**Client Encoding:** UTF8

**String Encoding:** Standard conforming strings enabled

**No encoding issues detected.**

---

## 13. Collation Assumptions

**Search Path:** `public`

**Default Tablespace:** `''` (default)

**No explicit collation settings.**

Uses database/cluster default collation.

---

## 14. Seed Data

**COPY statements with data:**

| Table | Rows |
|-------|------|
| player | 2 |
| player_buddies | 107 |
| player_buddy_win_poses | 4 |
| player_emblem_parts | 12 |
| player_emblems | 5 |
| player_line_colors | 9 |
| player_logins | 150 |
| player_mecha_colors | 28 |
| player_mecha_set_parts | 280 |
| player_mecha_sets | 28 |
| player_missions | 540 |
| player_options | 30 |
| player_progress | 82 |
| player_side_weapons | 24 |
| player_titles | 4 |
| player_weapon_set | 112 |
| player_weapon_set_slots | 364 |

**Total rows:** ~1,771

---

## 15. Potentially Destructive Statements

**None found.**

No `DROP`, `TRUNCATE`, or `DELETE` statements are present.

---

## 16. Hard-Coded Paths

**None found.**

No file system paths are referenced in the SQL.

---

## 17. COPY Statements

**17 COPY statements found:**

All COPY statements use `FROM stdin` format (pg_dump default).

**Data Format:** Tab-separated values with `\.` terminator.

---

## 18. Tables Referenced by JavaScript

**All 17 tables are referenced:**

| Table | Referenced In | Usage |
|-------|---------------|-------|
| player | playerProfile.js | SELECT, INSERT, UPDATE |
| player_buddies | playerProfile.js | SELECT, INSERT (ON CONFLICT) |
| player_buddy_win_poses | playerProfile.js | SELECT, INSERT (ON CONFLICT) |
| player_emblem_parts | playerProfile.js | SELECT, INSERT (ON CONFLICT) |
| player_emblems | playerProfile.js | SELECT, INSERT (ON CONFLICT) |
| player_line_colors | playerProfile.js | SELECT, INSERT (ON CONFLICT) |
| player_logins | playerProfile.js | SELECT, INSERT |
| player_mecha_colors | playerProfile.js | SELECT, INSERT (ON CONFLICT) |
| player_mecha_set_parts | playerProfile.js | SELECT, INSERT (ON CONFLICT) |
| player_mecha_sets | playerProfile.js | SELECT, INSERT (ON CONFLICT) |
| player_missions | playerProfile.js, battleRecorder.js | SELECT, INSERT (ON CONFLICT) |
| player_options | playerProfile.js | SELECT, INSERT (ON CONFLICT) |
| player_progress | playerProfile.js | SELECT, INSERT (ON CONFLICT) |
| player_side_weapons | playerProfile.js | SELECT, INSERT (ON CONFLICT) |
| player_titles | playerProfile.js | SELECT, INSERT (ON CONFLICT) |
| player_weapon_set | playerProfile.js | SELECT, INSERT (ON CONFLICT) |
| player_weapon_set_slots | playerProfile.js | SELECT, INSERT (ON CONFLICT) |

---

## 19. Tables Not Referenced by JavaScript

**None.**

All tables in the schema are actively used by the legacy JavaScript code.

---

## Import Compatibility Assessment

### Verdict: COMPATIBLE WITH MINOR ADJUSTMENTS

The legacy SQL dump is **fully compatible** with modern PostgreSQL versions (9.5+). The only required adjustments are:

1. **Create the `paradox` role** before importing
2. **Create the database** before importing

### No Schema Modifications Required

The SQL uses standard syntax that works across PostgreSQL versions. No alterations are needed for:
- Table definitions
- Column types
- Indexes
- Sequences
- Default values
- Seed data

### Import Command

```bash
# Create role and database
psql -U postgres -c "CREATE ROLE paradox WITH LOGIN PASSWORD 'changeme';"
psql -U postgres -c "CREATE DATABASE paradox OWNER paradox;"

# Import schema and data
psql -U paradox -d paradox -f legacy-js/paradox.sql
```

---

## Recommendations

1. **Add Foreign Keys (Optional):** Consider adding foreign key constraints for data integrity in the new system
2. **Add Indexes (Optional):** Consider adding indexes on frequently queried columns
3. **Validate Data:** Run `VACUUM ANALYZE` after import to update statistics
4. **Backup:** Create a backup before and after import
