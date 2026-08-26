# Starwing Paradox - Database Schema Map

> Source: `legacy-js/paradox.sql` (3201 lines)
> PostgreSQL 12.6 (Ubuntu 20.04)
> Owner: `paradox`

---

## Overview

- **Tables**: 15
- **Sequences**: 17 (auto-increment for all primary keys and FK-like IDs)
- **Test players**: 2 (IDs 10010 "ArcadeMachinist", 10011 "Lord Cereth")
- **No battle/match tables**: Battle results are not persisted in the schema

---

## Table: player

Main player profile table. PK: `player_id` (serial).

| Column | Type | Default | Notes |
|--------|------|---------|-------|
| player_id | integer (PK) | nextval('player_player_id_seq') | Auto-increment |
| nesys_id | varchar(22) NOT NULL | - | Banapassport/Nesys ID, unique per cabinet |
| player_name | varchar(50) | 'ＮｏＮａｍｅ' | Full-width default name |
| rank_id | integer | 0 | 1-on-1 rank |
| rank_id_2on2 | integer | 0 | 2-on-2 rank |
| title_id | integer | 0 | 1-on-1 title |
| title_id_2on2 | integer | 0 | 2-on-2 title |
| buddy_id | smallint | 0 | Active buddy |
| buddy_intimacy | smallint | 0 | Active buddy intimacy level |
| line_color_id | integer | 0 | Active line color |
| ranking_pref_name | varchar(30) | '東京' | Ranking prefecture |
| last_ranking_pref_name | varchar(30) | '東京' | Last ranking prefecture |
| match_mode_id | integer | 0 | Match mode |
| violation_point | integer | 0 | Anti-cheat violations |
| emblem_id | integer | 0 | Active emblem (1v1) |
| line_color_id_2on2 | integer | 0 | Active line color (2v2) |
| emblem_id_2on2 | integer | 0 | Active emblem (2v2) |
| birth_day | integer | 1 | Birthday day |
| birth_month | integer | 1 | Birthday month |
| mecha_set_id | integer | 0 | Active mecha set |
| side_weapon_id | integer | 0 | Active side weapon |
| mecha_preset_id | integer | 0 | Active mecha preset |
| rank_point | integer | 0 | 1v1 rank points |
| max_rank_id | integer | 0 | Max rank achieved (1v1) |
| rank_point_2on2 | integer | 0 | 2v2 rank points |
| max_rank_id_2on2 | integer | 0 | Max rank achieved (2v2) |

**Unique index**: None on nesys_id (potential duplicate issue)

---

## Table: player_buddies

Buddy system key-value store. PK: `id` (serial).

| Column | Type | Default | Notes |
|--------|------|---------|-------|
| id | integer (PK) | nextval('player_buddies_id_seq') | Auto-increment |
| player_id | integer NOT NULL | - | FK to player |
| buddy_id | integer NOT NULL | - | Buddy slot (1-6) |
| buddy_key | varchar(35) NOT NULL | - | Key name (e.g. "skill_id1", "intimacy", "win_pose_id") |
| buddy_value | varchar(35) | 0 | Value (string or numeric) |

**Unique index**: (player_id, buddy_id, buddy_key)

**Known keys**: intimacy_level_id, intimacy, skill_id1, skill_id2, skill_id3, win_pose_id, win_pose_2on2_id, login_days, use_count, use_time, memorial_login_days, winning_streaks, winning_streaks_2on2, status, is_first, high_touch_continue_count

---

## Table: player_buddy_win_poses

Win pose unlocks per buddy. PK: `id` (serial).

| Column | Type | Default | Notes |
|--------|------|---------|-------|
| id | integer (PK) | nextval('buddy_win_poses_id_seq') | Auto-increment |
| player_id | integer NOT NULL | - | FK to player |
| buddy_id | integer NOT NULL | - | Buddy slot |
| win_pose_id | integer NOT NULL | - | Win pose ID |
| status | integer | 0 | Unlock status (4 = unlocked) |

**Unique index**: (player_id, buddy_id, win_pose_id)

---

## Table: player_emblem_parts

Emblem part unlocks. PK: `id` (serial).

| Column | Type | Default | Notes |
|--------|------|---------|-------|
| id | integer (PK) | nextval('player_emblem_parts_id_seq') | Auto-increment |
| player_id | integer NOT NULL | - | FK to player |
| part_id | integer NOT NULL | - | Emblem part ID |
| status | integer | 0 | Unlock status (4 = unlocked) |

**Unique index**: (player_id, part_id)

---

## Table: player_emblems

Emblem configurations. PK: `id` (serial).

| Column | Type | Default | Notes |
|--------|------|---------|-------|
| id | integer (PK) | nextval('player_emblems_id_seq') | Auto-increment |
| player_id | integer NOT NULL | - | FK to player |
| emblem_id | integer NOT NULL | - | Emblem slot ID |
| outline_part_id | integer NOT NULL | - | Outline part |
| outline_offset_x | integer NOT NULL | - | Outline X offset |
| outline_offset_y | integer NOT NULL | - | Outline Y offset |
| outline_scale_x | integer NOT NULL | - | Outline X scale |
| outline_scale_y | integer NOT NULL | - | Outline Y scale |
| outline_angle | integer NOT NULL | - | Outline rotation |
| main_design_part_id | integer NOT NULL | - | Main design part |
| main_design_offset_x | integer NOT NULL | - | Main X offset |
| main_design_offset_y | integer NOT NULL | - | Main Y offset |
| main_design_scale_x | integer NOT NULL | - | Main X scale |
| main_design_scale_y | integer NOT NULL | - | Main Y scale |
| main_design_angle | integer NOT NULL | - | Main rotation |
| sub_design_part_id | integer NOT NULL | - | Sub design part |
| sub_design_offset_x | integer NOT NULL | - | Sub X offset |
| sub_design_offset_y | integer NOT NULL | - | Sub Y offset |
| sub_design_scale_x | integer NOT NULL | - | Sub X scale |
| sub_design_scale_y | integer NOT NULL | - | Sub Y scale |
| sub_design_angle | integer NOT NULL | - | Sub rotation |
| status | integer | 0 | Status |
| editable | boolean | false | User-editable flag |

**Unique index**: (player_id, emblem_id)

---

## Table: player_line_colors

Line color unlocks. PK: `id` (serial).

| Column | Type | Default | Notes |
|--------|------|---------|-------|
| id | integer (PK) | nextval('player_line_colors_id_seq') | Auto-increment |
| player_id | integer NOT NULL | - | FK to player |
| line_color_id | integer NOT NULL | - | Line color ID |
| status | integer | 0 | Unlock status (4 = unlocked) |

**Unique index**: (player_id, line_color_id)

---

## Table: player_logins

Login audit trail. PK: `id` (serial).

| Column | Type | Default | Notes |
|--------|------|---------|-------|
| id | integer (PK) | nextval('player_logins_id_seq') | Auto-increment |
| player_id | integer NOT NULL | - | FK to player |
| ip_addr | inet NOT NULL | - | Client IP address |
| location_id | integer | 0 | Cabinet location |
| client_version | integer | 0 | Client version |
| data_version | integer | 0 | Data version |
| ts_when | timestamp NOT NULL | - | Login timestamp |

**No unique index** (multiple logins per player allowed)

---

## Table: player_mecha_colors

Mecha color unlocks. PK: `id` (serial).

| Column | Type | Default | Notes |
|--------|------|---------|-------|
| id | integer (PK) | nextval('mecha_colors_id_seq') | Auto-increment |
| player_id | integer NOT NULL | - | FK to player |
| mecha_color_id | integer NOT NULL | - | Mecha color ID |
| status | integer | 0 | Unlock status (4 = unlocked) |

**Unique index**: (player_id, mecha_color_id)

---

## Table: player_mecha_set_parts

Mecha set part configurations. PK: `id` (serial).

| Column | Type | Default | Notes |
|--------|------|---------|-------|
| id | integer (PK) | nextval('player_mecha_set_parts_id_seq') | Auto-increment |
| player_id | integer NOT NULL | - | FK to player |
| mecha_set_id | integer NOT NULL | - | Mecha set ID |
| part_id | integer NOT NULL | - | Part slot (1-5) |
| mecha_id | integer NOT NULL | - | Mecha model ID |
| design_id | integer | 0 | Design variant |
| color_id | integer | 0 | Color variant |

**Unique index**: (player_id, mecha_set_id, part_id)

---

## Table: player_mecha_sets

Mecha set configurations. PK: `id` (serial).

| Column | Type | Default | Notes |
|--------|------|---------|-------|
| id | integer (PK) | nextval('player_mecha_sets_id_seq') | Auto-increment |
| player_id | integer NOT NULL | - | FK to player |
| mecha_set_id | integer NOT NULL | - | Mecha set ID |
| mecha_setbonus_id | integer NOT NULL | - | Set bonus ID |
| weapon_set_id | integer NOT NULL | - | Weapon set ID |
| is_decal | boolean | false | Decal applied |
| favorite | boolean | false | Favorite flag |
| use_count | integer | 0 | Times used |
| use_time | integer | 0 | Total use time |
| status | integer | 0 | Status |
| win_count | integer | NULL | Win count (nullable) |
| winning_streaks | integer | NULL | Winning streaks (nullable) |

**Unique index**: (player_id, mecha_set_id)

---

## Table: player_missions

Mission progress tracking. PK: `id` (serial).

| Column | Type | Default | Notes |
|--------|------|---------|-------|
| id | integer (PK) | nextval('player_missions_id_seq') | Auto-increment |
| player_id | integer NOT NULL | - | FK to player |
| mission_id | integer NOT NULL | - | Mission ID |
| clear_count | integer | 0 | Times cleared |
| clear_num | integer | 0 | Progress counter |
| status | integer | 0 | Status |
| mission_status | integer | 0 | Mission status (201=active, 400=completed) |

**Unique index**: (player_id, mission_id)

---

## Table: player_options

Player settings key-value store. PK: `id` (serial).

| Column | Type | Default | Notes |
|--------|------|---------|-------|
| id | integer (PK) | nextval('player_options_id_seq') | Auto-increment |
| player_id | integer NOT NULL | - | FK to player |
| option_key | varchar(35) NOT NULL | - | Setting name |
| value_num | integer | 0 | Numeric value |

**Unique index**: (player_id, option_key)

**Known option keys**: language, camera_control_parallel, camera_control_vertical, pedal_control, chair_shake, assist_control, assist_show, volume_bgm, volume_se, volume_voice, vibration, battle_log_show, sorting_effect_display, map_displa (note: typo, missing 'y'), chaild_mode (note: typo, should be 'child')

---

## Table: player_progress

Tutorial/feature unlock progress. PK: `id` (serial).

| Column | Type | Default | Notes |
|--------|------|---------|-------|
| id | integer (PK) | nextval('player_progress_id_seq') | Auto-increment |
| player_id | integer NOT NULL | - | FK to player |
| progress_key | varchar(35) NOT NULL | - | Progress name |
| status | smallint | 0 | Status (0=locked, 2=unlocked) |

**Unique index**: (player_id, progress_key)

**Known progress keys**: tutorial, buddy_present, customize, player_customize, buddy_customize, mecha_customize, role_customize, shop, quest, buddy_skill, main_menu, present, mecha_shop, weapon_shop, emblem_shop, win_pose_shop, line_color_shop, symbol_chat_shop, parts_color_shop, player_emblem_customize, player_title_customize, preset_customize, win_pose, line_color, national_match, coop, boss, mission, player_customize_2on2, buddy_customize_2on2, mecha_customize_2on2, player_emblem_customize_2on2, player_title_customize_2on2, coop_2on2, mission_2on2, tutorial_2on2, tutorial_2on2_2nd, tutorial_2on2_finish

---

## Table: player_side_weapons

Side weapon unlocks. PK: `id` (serial).

| Column | Type | Default | Notes |
|--------|------|---------|-------|
| id | integer (PK) | nextval('player_side_weapons_id_seq') | Auto-increment |
| player_id | integer NOT NULL | - | FK to player |
| side_weapon_id | integer NOT NULL | - | Side weapon ID |
| use_count | integer | 0 | Times used |
| use_time | integer | 0 | Total use time |
| status | integer | 0 | Unlock status |

**Unique index**: (player_id, side_weapon_id)

---

## Table: player_titles

Title unlocks. PK: `id` (serial).

| Column | Type | Default | Notes |
|--------|------|---------|-------|
| id | integer (PK) | nextval('player_titles_id_seq') | Auto-increment |
| player_id | integer NOT NULL | - | FK to player |
| title_id | integer NOT NULL | - | Title ID |
| status | integer | 0 | Unlock status (4 = unlocked) |

**Unique index**: (player_id, title_id)

---

## Table: player_weapon_set

Weapon set unlocks. PK: `id` (serial).

| Column | Type | Default | Notes |
|--------|------|---------|-------|
| id | integer (PK) | nextval('weapon_set_id_seq') | Auto-increment |
| player_id | integer NOT NULL | - | FK to player |
| weapon_set_id | integer NOT NULL | - | Weapon set ID |
| use_count | integer | 0 | Times used |
| use_time | integer | 0 | Total use time |
| status | integer | 0 | Unlock status |

**Unique index**: (player_id, weapon_set_id)

---

## Table: player_weapon_set_slots

Weapon slot configurations. PK: `id` (serial).

| Column | Type | Default | Notes |
|--------|------|---------|-------|
| id | integer (PK) | nextval('player_weapon_set_slots_id_seq') | Auto-increment |
| player_id | integer NOT NULL | - | FK to player |
| weapon_set_id | integer NOT NULL | - | FK to weapon_set |
| slot_id | integer NOT NULL | - | Slot index (0-based) |
| weapon_id | integer NOT NULL | - | Weapon ID |
| use_count | integer | 0 | Times used |
| use_time | integer | 0 | Total use time |

**Unique index**: (player_id, weapon_set_id, slot_id)

---

## Test Data Summary

### Player 10010 (ArcadeMachinist)
- Rank: 20 (1v1), 20 (2v2)
- 6 buddies fully configured
- 14 mecha sets, 56 weapon sets
- ~350 missions tracked
- Login timestamps: 2021-12-04 to 2022-04-05

### Player 10011 (Lord Cereth)
- Rank: 10 (1v1), 10 (2v2)
- 6 buddies fully configured
- 14 mecha sets
- ~350 missions tracked

### Sequence Values (as of dump)
| Sequence | Current Value |
|----------|---------------|
| player_player_id_seq | 10011 |
| player_player_id_seq | 10011 |
| player_buddies_id_seq | 15456 |
| player_missions_id_seq | 2629 |
| player_progress_id_seq | 4907 |
| player_mecha_set_parts_id_seq | 700 |
| player_mecha_sets_id_seq | 140 |
| player_weapon_set_slots_id_seq | 728 |
| weapon_set_id_seq | 224 |

---

## Missing Tables (not in schema)

The following data types are referenced in `playerSaveGameData` or `API-NOTES.txt` but have no corresponding table:

- quests (mentioned in API-NOTES.txt body)
- game_moneys (returned in battle response)
- present_items
- greetings
- buddy_greetings
- symbol_chats
- symbol_chat_slots
- cockpit_items
- mecha_presets
- mecha_preset_parts
- weapon_roles
- weapon_role_presets
- weapon_role_preset_slots
- weapons
