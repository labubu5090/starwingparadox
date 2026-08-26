-- Legacy Minimum Seed Schema for Integration Testing
-- Source: legacy-js/paradox.sql
--
-- This file contains only the minimum schema and seed data required for
-- integration testing of database-dependent routes. Derived from the
-- legacy PostgreSQL dump.
--
-- Tables included: player, player_buddies, player_logins, player_progress,
-- player_missions, player_options, player_titles, player_line_colors,
-- player_emblems, player_emblem_parts, player_mecha_sets, player_mecha_set_parts,
-- player_mecha_colors, player_weapon_set, player_weapon_set_slots,
-- player_side_weapons, player_buddy_win_poses.
--
-- Seed data: Two test players (10010, 10011) from paradox.sql.
-- Source evidence: legacy-js/js/starwing.js playerProfile.js

-- =========================================================================
-- Schema: player (core table)
-- Source: paradox.sql lines 97-127
-- Routes: POST /player/profile/load (starwing.js:488-507)
--         POST /player/login (starwing.js:509-531)
--         POST /player/register (starwing.js:557-574)
--         POST /game_data/load (starwing.js:677-698)
--         POST /game_data/save (starwing.js:700-720)
-- =========================================================================

CREATE TABLE IF NOT EXISTS player (
    player_id INTEGER PRIMARY KEY,
    nesys_id VARCHAR(22) NOT NULL,
    player_name VARCHAR(50) DEFAULT 'ＮｏＮａｍｅ',
    rank_id INTEGER DEFAULT 0,
    rank_id_2on2 INTEGER DEFAULT 0,
    title_id INTEGER DEFAULT 0,
    title_id_2on2 INTEGER DEFAULT 0,
    buddy_id SMALLINT DEFAULT 0,
    buddy_intimacy SMALLINT DEFAULT 0,
    line_color_id INTEGER DEFAULT 0,
    ranking_pref_name VARCHAR(30) DEFAULT '東京',
    last_ranking_pref_name VARCHAR(30) DEFAULT '東京',
    match_mode_id INTEGER DEFAULT 0,
    violation_point INTEGER DEFAULT 0,
    emblem_id INTEGER DEFAULT 0,
    line_color_id_2on2 INTEGER DEFAULT 0,
    emblem_id_2on2 INTEGER DEFAULT 0,
    birth_day INTEGER DEFAULT 1,
    birth_month INTEGER DEFAULT 1,
    mecha_set_id INTEGER DEFAULT 0,
    side_weapon_id INTEGER DEFAULT 0,
    mecha_preset_id INTEGER DEFAULT 0,
    rank_point INTEGER DEFAULT 0,
    max_rank_id INTEGER DEFAULT 0,
    rank_point_2on2 INTEGER DEFAULT 0,
    max_rank_id_2on2 INTEGER DEFAULT 0
);

-- =========================================================================
-- Schema: player_logins
-- Source: paradox.sql lines 297-308
-- Routes: POST /player/login — INSERT (playerProfile.js:353)
--         POST /game_data/load — SELECT (playerProfile.js:94-101)
-- =========================================================================

CREATE TABLE IF NOT EXISTS player_logins (
    id SERIAL PRIMARY KEY,
    player_id INTEGER NOT NULL,
    ip_addr INET NOT NULL,
    location_id INTEGER DEFAULT 0,
    client_version INTEGER DEFAULT 0,
    data_version INTEGER DEFAULT 0,
    ts_when TIMESTAMP WITHOUT TIME ZONE NOT NULL
);

-- =========================================================================
-- Schema: player_buddies
-- Source: paradox.sql lines 132-145
-- Routes: POST /game_data/load — SELECT (playerProfile.js:111)
--         POST /game_data/save — UPSERT (playerProfile.js:452-480)
-- Quirk: Composite PK on (player_id, buddy_id, buddy_key) via ON CONFLICT
-- =========================================================================

CREATE TABLE IF NOT EXISTS player_buddies (
    id SERIAL PRIMARY KEY,
    player_id INTEGER NOT NULL,
    buddy_id INTEGER NOT NULL,
    buddy_key VARCHAR(35) NOT NULL,
    buddy_value VARCHAR(35) DEFAULT '0'
);

-- =========================================================================
-- Schema: player_progress
-- Source: paradox.sql lines 516-524
-- Routes: POST /player/profile/load — SELECT (playerProfile.js:331)
--         POST /player/login — SELECT (playerProfile.js:358-362)
--         POST /player/register — UPSERT (playerProfile.js:425-431)
--         POST /game_data/load — SELECT (playerProfile.js:130)
--         POST /game_data/save — UPSERT (playerProfile.js:481-492)
-- Quirk: ON CONFLICT (player_id, progress_key) DO UPDATE
-- =========================================================================

CREATE TABLE IF NOT EXISTS player_progress (
    id SERIAL PRIMARY KEY,
    player_id INTEGER NOT NULL,
    progress_key VARCHAR(35) NOT NULL,
    status SMALLINT DEFAULT 0,
    UNIQUE (player_id, progress_key)
);

-- =========================================================================
-- Schema: player_missions
-- Source: paradox.sql lines 419-430
-- Routes: POST /game_data/load — SELECT (playerProfile.js:144)
--         POST /game_data/load/mission — SELECT (playerProfile.js:74-85)
--         POST /game_data/save — UPSERT (playerProfile.js:493-502)
-- Quirk: ON CONFLICT (player_id, mission_id) DO UPDATE
-- =========================================================================

CREATE TABLE IF NOT EXISTS player_missions (
    id SERIAL PRIMARY KEY,
    player_id INTEGER NOT NULL,
    mission_id INTEGER NOT NULL,
    clear_count INTEGER DEFAULT 0,
    clear_num INTEGER DEFAULT 0,
    status INTEGER DEFAULT 0,
    mission_status INTEGER DEFAULT 0,
    UNIQUE (player_id, mission_id)
);

-- =========================================================================
-- Schema: player_options
-- Source: paradox.sql lines 458-466
-- Routes: POST /game_data/load — SELECT (playerProfile.js:137)
--         POST /game_data/save — UPSERT (playerProfile.js:442-451)
-- Quirk: ON CONFLICT (player_id, option_key) DO UPDATE
-- =========================================================================

CREATE TABLE IF NOT EXISTS player_options (
    id SERIAL PRIMARY KEY,
    player_id INTEGER NOT NULL,
    option_key VARCHAR(35) NOT NULL,
    value_num INTEGER DEFAULT 0,
    UNIQUE (player_id, option_key)
);

-- =========================================================================
-- Schema: player_titles
-- Source: paradox.sql lines 590-598
-- Routes: POST /game_data/load — SELECT (playerProfile.js:212)
--         POST /game_data/save — UPSERT (playerProfile.js:503-512)
-- Quirk: ON CONFLICT (player_id, title_id) DO UPDATE
-- =========================================================================

CREATE TABLE IF NOT EXISTS player_titles (
    id SERIAL PRIMARY KEY,
    player_id INTEGER NOT NULL,
    title_id INTEGER NOT NULL,
    status INTEGER DEFAULT 0,
    UNIQUE (player_id, title_id)
);

-- =========================================================================
-- Schema: player_line_colors
-- Source: paradox.sql lines 260-269
-- Routes: POST /game_data/load — SELECT (playerProfile.js:221)
--         POST /game_data/save — UPSERT (playerProfile.js:609-619)
-- Quirk: ON CONFLICT (player_id, line_color_id) DO UPDATE
-- =========================================================================

CREATE TABLE IF NOT EXISTS player_line_colors (
    id SERIAL PRIMARY KEY,
    player_id INTEGER NOT NULL,
    line_color_id INTEGER NOT NULL,
    status INTEGER DEFAULT 0,
    UNIQUE (player_id, line_color_id)
);

-- =========================================================================
-- Schema: player_emblems
-- Source: paradox.sql lines 206-233
-- Routes: POST /game_data/load — SELECT (playerProfile.js:163)
--         POST /game_data/save — UPSERT (playerProfile.js:513-558)
-- Quirk: 22 columns per row. ON CONFLICT (player_id, emblem_id) DO UPDATE
-- =========================================================================

CREATE TABLE IF NOT EXISTS player_emblems (
    id SERIAL PRIMARY KEY,
    player_id INTEGER NOT NULL,
    emblem_id INTEGER NOT NULL,
    outline_part_id INTEGER NOT NULL,
    outline_offset_x INTEGER NOT NULL,
    outline_offset_y INTEGER NOT NULL,
    outline_scale_x INTEGER NOT NULL,
    outline_scale_y INTEGER NOT NULL,
    outline_angle INTEGER NOT NULL,
    main_design_part_id INTEGER NOT NULL,
    main_design_offset_x INTEGER NOT NULL,
    main_design_offset_y INTEGER NOT NULL,
    main_design_scale_x INTEGER NOT NULL,
    main_design_scale_y INTEGER NOT NULL,
    main_design_angle INTEGER NOT NULL,
    sub_design_part_id INTEGER NOT NULL,
    sub_design_offset_x INTEGER NOT NULL,
    sub_design_offset_y INTEGER NOT NULL,
    sub_design_scale_x INTEGER NOT NULL,
    sub_design_scale_y INTEGER NOT NULL,
    sub_design_angle INTEGER NOT NULL,
    status INTEGER DEFAULT 0,
    editable BOOLEAN DEFAULT FALSE,
    UNIQUE (player_id, emblem_id)
);

-- =========================================================================
-- Schema: player_emblem_parts
-- Source: paradox.sql lines 170-178
-- Routes: POST /game_data/load — SELECT (playerProfile.js:191)
--         POST /game_data/save — UPSERT (playerProfile.js:559-568)
-- Quirk: ON CONFLICT (player_id, part_id) DO UPDATE
-- =========================================================================

CREATE TABLE IF NOT EXISTS player_emblem_parts (
    id SERIAL PRIMARY KEY,
    player_id INTEGER NOT NULL,
    part_id INTEGER NOT NULL,
    status INTEGER DEFAULT 0,
    UNIQUE (player_id, part_id)
);

-- =========================================================================
-- Schema: player_mecha_sets
-- Source: paradox.sql lines 375-391
-- Routes: POST /game_data/load — SELECT (playerProfile.js:237)
--         POST /game_data/save — UPSERT (playerProfile.js:569-583)
-- Quirk: ON CONFLICT (player_id, mecha_set_id) DO UPDATE
-- =========================================================================

CREATE TABLE IF NOT EXISTS player_mecha_sets (
    id SERIAL PRIMARY KEY,
    player_id INTEGER NOT NULL,
    mecha_set_id INTEGER NOT NULL,
    mecha_setbonus_id INTEGER NOT NULL,
    weapon_set_id INTEGER NOT NULL,
    is_decal BOOLEAN DEFAULT FALSE,
    favorite BOOLEAN DEFAULT FALSE,
    use_count INTEGER DEFAULT 0,
    use_time INTEGER DEFAULT 0,
    status INTEGER DEFAULT 0,
    win_count INTEGER,
    winning_streaks INTEGER,
    UNIQUE (player_id, mecha_set_id)
);

-- =========================================================================
-- Schema: player_mecha_set_parts
-- Source: paradox.sql lines 336-347
-- Routes: POST /game_data/load — SELECT (playerProfile.js:246)
--         POST /game_data/save — UPSERT (playerProfile.js:584-596)
-- Quirk: ON CONFLICT (player_id, mecha_set_id, part_id) DO UPDATE
-- =========================================================================

CREATE TABLE IF NOT EXISTS player_mecha_set_parts (
    id SERIAL PRIMARY KEY,
    player_id INTEGER NOT NULL,
    mecha_set_id INTEGER NOT NULL,
    part_id INTEGER NOT NULL,
    mecha_id INTEGER NOT NULL,
    design_id INTEGER DEFAULT 0,
    color_id INTEGER DEFAULT 0,
    UNIQUE (player_id, mecha_set_id, part_id)
);

-- =========================================================================
-- Schema: player_mecha_colors
-- Source: paradox.sql lines 60-69
-- Routes: POST /game_data/load — SELECT (playerProfile.js:254)
--         POST /game_data/save — UPSERT (playerProfile.js:620-629)
-- Quirk: ON CONFLICT (player_id, mecha_color_id) DO UPDATE
-- =========================================================================

CREATE TABLE IF NOT EXISTS player_mecha_colors (
    id SERIAL PRIMARY KEY,
    player_id INTEGER NOT NULL,
    mecha_color_id INTEGER NOT NULL,
    status INTEGER DEFAULT 0,
    UNIQUE (player_id, mecha_color_id)
);

-- =========================================================================
-- Schema: player_weapon_set
-- Source: paradox.sql lines 626-636
-- Routes: POST /game_data/load — SELECT (playerProfile.js:264)
--         POST /game_data/save — UPSERT (playerProfile.js:630-639)
-- Quirk: ON CONFLICT (player_id, weapon_set_id) DO UPDATE
-- =========================================================================

CREATE TABLE IF NOT EXISTS player_weapon_set (
    id SERIAL PRIMARY KEY,
    player_id INTEGER NOT NULL,
    weapon_set_id INTEGER NOT NULL,
    use_count INTEGER DEFAULT 0,
    use_time INTEGER DEFAULT 0,
    status INTEGER DEFAULT 0,
    UNIQUE (player_id, weapon_set_id)
);

-- =========================================================================
-- Schema: player_weapon_set_slots
-- Source: paradox.sql lines 642-653
-- Routes: POST /game_data/load — SELECT (playerProfile.js:272)
--         POST /game_data/save — UPSERT (playerProfile.js:640-650)
-- Quirk: ON CONFLICT (player_id, weapon_set_id, slot_id) DO UPDATE
-- =========================================================================

CREATE TABLE IF NOT EXISTS player_weapon_set_slots (
    id SERIAL PRIMARY KEY,
    player_id INTEGER NOT NULL,
    weapon_set_id INTEGER NOT NULL,
    slot_id INTEGER NOT NULL,
    weapon_id INTEGER NOT NULL,
    use_count INTEGER DEFAULT 0,
    use_time INTEGER DEFAULT 0,
    UNIQUE (player_id, weapon_set_id, slot_id)
);

-- =========================================================================
-- Schema: player_side_weapons
-- Source: paradox.sql lines 550-562
-- Routes: POST /game_data/load — SELECT (playerProfile.js:282)
--         POST /game_data/save — UPSERT (playerProfile.js:651-660)
-- Quirk: ON CONFLICT (player_id, side_weapon_id) DO UPDATE
-- =========================================================================

CREATE TABLE IF NOT EXISTS player_side_weapons (
    id SERIAL PRIMARY KEY,
    player_id INTEGER NOT NULL,
    side_weapon_id INTEGER NOT NULL,
    use_count INTEGER DEFAULT 0,
    use_time INTEGER DEFAULT 0,
    status INTEGER DEFAULT 0,
    UNIQUE (player_id, side_weapon_id)
);

-- =========================================================================
-- Schema: player_buddy_win_poses
-- Source: paradox.sql lines 24-33
-- Routes: POST /game_data/load — SELECT (playerProfile.js:154)
--         POST /game_data/save — UPSERT (playerProfile.js:597-608)
-- Quirk: ON CONFLICT (player_id, buddy_id, win_pose_id) DO UPDATE
-- =========================================================================

CREATE TABLE IF NOT EXISTS player_buddy_win_poses (
    id SERIAL PRIMARY KEY,
    player_id INTEGER NOT NULL,
    buddy_id INTEGER NOT NULL,
    win_pose_id INTEGER NOT NULL,
    status INTEGER DEFAULT 0,
    UNIQUE (player_id, buddy_id, win_pose_id)
);

-- =========================================================================
-- Minimum Seed Data
-- Source: paradox.sql lines 822-828 (COPY player)
-- These are the two test players from the legacy database dump.
-- =========================================================================

INSERT INTO player (player_id, nesys_id, player_name, rank_id, rank_id_2on2,
    title_id, title_id_2on2, buddy_id, buddy_intimacy, line_color_id,
    emblem_id, line_color_id_2on2, emblem_id_2on2, mecha_set_id,
    side_weapon_id, mecha_preset_id, rank_point, max_rank_id,
    rank_point_2on2, max_rank_id_2on2)
VALUES
    (10010, '7020392000000000', 'ArcadeMachinist', 20, 20,
     100001, 100001, 5, 2, 1,
     1, 100002, 1, 1001,
     2, 0, 0, 0, 300, 0),
    (10011, '7020392000000001', 'Lord Cereth', 10, 10,
     0, 100000, 2, 0, 1,
     1, 100001, 0, 1001,
     2, 0, 0, 0, 300, 0)
ON CONFLICT (player_id) DO NOTHING;

-- Minimum buddy data for player 10010 (buddy_id=1)
INSERT INTO player_buddies (player_id, buddy_id, buddy_key, buddy_value)
VALUES
    (10010, 1, 'intimacy_level_id', '1'),
    (10010, 1, 'intimacy', '0'),
    (10010, 1, 'skill_id1', '14'),
    (10010, 1, 'skill_id2', '0'),
    (10010, 1, 'skill_id3', '0'),
    (10010, 1, 'win_pose_id', '1'),
    (10010, 1, 'win_pose_2on2_id', '11'),
    (10010, 1, 'login_days', '0'),
    (10010, 1, 'use_time', '0'),
    (10010, 1, 'use_count', '0'),
    (10010, 1, 'memorial_login_days', '0'),
    (10010, 1, 'winning_streaks', '0'),
    (10010, 1, 'winning_streaks_2on2', '0'),
    (10010, 1, 'status', '4'),
    (10010, 1, 'is_first', 'false'),
    (10010, 1, 'high_touch_continue_count', '0')
ON CONFLICT DO NOTHING;

-- Minimum login for player 10010
INSERT INTO player_logins (player_id, ip_addr, location_id, client_version, data_version, ts_when)
VALUES
    (10010, '127.0.0.1', 77, 70571, 70571, '2026-01-01 00:00:00')
ON CONFLICT DO NOTHING;

-- Minimum progress for player 10010
INSERT INTO player_progress (player_id, progress_key, status)
VALUES
    (10010, 'tutorial_complete', 1)
ON CONFLICT DO NOTHING;

-- Minimum mission for player 10010
INSERT INTO player_missions (player_id, mission_id, clear_count, clear_num, status, mission_status)
VALUES
    (10010, 136001, 0, 6, 4, 400)
ON CONFLICT DO NOTHING;

-- Minimum title for player 10010
INSERT INTO player_titles (player_id, title_id, status)
VALUES
    (10010, 100001, 4)
ON CONFLICT DO NOTHING;

-- Minimum line color for player 10010
INSERT INTO player_line_colors (player_id, line_color_id, status)
VALUES
    (10010, 100001, 4)
ON CONFLICT DO NOTHING;

-- Minimum emblem for player 10010
INSERT INTO player_emblems (player_id, emblem_id,
    outline_part_id, outline_offset_x, outline_offset_y,
    outline_scale_x, outline_scale_y, outline_angle,
    main_design_part_id, main_design_offset_x, main_design_offset_y,
    main_design_scale_x, main_design_scale_y, main_design_angle,
    sub_design_part_id, sub_design_offset_x, sub_design_offset_y,
    sub_design_scale_x, sub_design_scale_y, sub_design_angle,
    status, editable)
VALUES
    (10010, 2, 0, 0, 0, 1, 1, 0, 120091, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 4, FALSE)
ON CONFLICT DO NOTHING;

-- Minimum emblem part for player 10010
INSERT INTO player_emblem_parts (player_id, part_id, status)
VALUES
    (10010, 110001, 4)
ON CONFLICT DO NOTHING;

-- Minimum mecha set for player 10010
INSERT INTO player_mecha_sets (player_id, mecha_set_id, mecha_setbonus_id,
    weapon_set_id, is_decal, favorite, use_count, use_time, status)
VALUES
    (10010, 1001, 1, 100, FALSE, FALSE, 0, 0, 4)
ON CONFLICT DO NOTHING;

-- Minimum mecha set parts for player 10010, mecha_set 1001
INSERT INTO player_mecha_set_parts (player_id, mecha_set_id, part_id, mecha_id, design_id, color_id)
VALUES
    (10010, 1001, 1, 1, 1, 0),
    (10010, 1001, 2, 1, 1, 0),
    (10010, 1001, 3, 1, 1, 0),
    (10010, 1001, 4, 1, 1, 0),
    (10010, 1001, 5, 1, 1, 0)
ON CONFLICT DO NOTHING;

-- Minimum mecha color for player 10010
INSERT INTO player_mecha_colors (player_id, mecha_color_id, status)
VALUES
    (10010, 0, 4)
ON CONFLICT DO NOTHING;

-- Minimum weapon set for player 10010
INSERT INTO player_weapon_set (player_id, weapon_set_id, use_count, use_time, status)
VALUES
    (10010, 100, 0, 0, 4)
ON CONFLICT DO NOTHING;

-- Minimum buddy win pose for player 10010
INSERT INTO player_buddy_win_poses (player_id, buddy_id, win_pose_id, status)
VALUES
    (10010, 1, 11, 4)
ON CONFLICT DO NOTHING;
