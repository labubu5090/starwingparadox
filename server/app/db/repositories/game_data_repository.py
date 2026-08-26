"""Game data repository for loading/saving player game data."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.player_buddies import PlayerBuddy
from app.db.models.player_buddy_win_poses import PlayerBuddyWinPose
from app.db.models.player_emblem_parts import PlayerEmblemPart
from app.db.models.player_emblems import PlayerEmblem
from app.db.models.player_line_colors import PlayerLineColor
from app.db.models.player_mecha_colors import PlayerMechaColor
from app.db.models.player_mecha_set_parts import PlayerMechaSetPart
from app.db.models.player_mecha_sets import PlayerMechaSet
from app.db.models.player_missions import PlayerMission
from app.db.models.player_options import PlayerOption
from app.db.models.player_progress import PlayerProgress
from app.db.models.player_side_weapons import PlayerSideWeapon
from app.db.models.player_titles import PlayerTitle
from app.db.models.player_weapon_set import PlayerWeaponSet
from app.db.models.player_weapon_set_slots import PlayerWeaponSetSlot


class GameDataRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_buddies(self, player_id: int) -> list[PlayerBuddy]:
        result = await self.session.execute(
            select(PlayerBuddy).where(PlayerBuddy.player_id == player_id)
        )
        return list(result.scalars().all())

    async def upsert_buddy(
        self, player_id: int, buddy_id: int, buddy_key: str, buddy_value: str = "0"
    ) -> PlayerBuddy:
        result = await self.session.execute(
            select(PlayerBuddy).where(
                PlayerBuddy.player_id == player_id,
                PlayerBuddy.buddy_id == buddy_id,
                PlayerBuddy.buddy_key == buddy_key,
            )
        )
        buddy = result.scalar_one_or_none()
        if buddy:
            buddy.buddy_value = buddy_value
        else:
            buddy = PlayerBuddy(
                player_id=player_id,
                buddy_id=buddy_id,
                buddy_key=buddy_key,
                buddy_value=buddy_value,
            )
            self.session.add(buddy)
        await self.session.flush()
        return buddy

    async def get_buddy_win_poses(self, player_id: int) -> list[PlayerBuddyWinPose]:
        result = await self.session.execute(
            select(PlayerBuddyWinPose).where(PlayerBuddyWinPose.player_id == player_id)
        )
        return list(result.scalars().all())

    async def upsert_buddy_win_pose(
        self, player_id: int, buddy_id: int, win_pose_id: int, status: int = 0
    ) -> PlayerBuddyWinPose:
        result = await self.session.execute(
            select(PlayerBuddyWinPose).where(
                PlayerBuddyWinPose.player_id == player_id,
                PlayerBuddyWinPose.buddy_id == buddy_id,
                PlayerBuddyWinPose.win_pose_id == win_pose_id,
            )
        )
        pose = result.scalar_one_or_none()
        if pose:
            pose.status = status
        else:
            pose = PlayerBuddyWinPose(
                player_id=player_id,
                buddy_id=buddy_id,
                win_pose_id=win_pose_id,
                status=status,
            )
            self.session.add(pose)
        await self.session.flush()
        return pose

    async def get_progress(self, player_id: int) -> list[PlayerProgress]:
        result = await self.session.execute(
            select(PlayerProgress).where(PlayerProgress.player_id == player_id)
        )
        return list(result.scalars().all())

    async def upsert_progress(
        self, player_id: int, progress_key: str, status: int = 0
    ) -> PlayerProgress:
        result = await self.session.execute(
            select(PlayerProgress).where(
                PlayerProgress.player_id == player_id,
                PlayerProgress.progress_key == progress_key,
            )
        )
        prog = result.scalar_one_or_none()
        if prog:
            prog.status = status
        else:
            prog = PlayerProgress(player_id=player_id, progress_key=progress_key, status=status)
            self.session.add(prog)
        await self.session.flush()
        return prog

    async def get_options(self, player_id: int) -> list[PlayerOption]:
        result = await self.session.execute(
            select(PlayerOption).where(PlayerOption.player_id == player_id)
        )
        return list(result.scalars().all())

    async def upsert_option(
        self, player_id: int, option_key: str, value_num: int = 0
    ) -> PlayerOption:
        result = await self.session.execute(
            select(PlayerOption).where(
                PlayerOption.player_id == player_id,
                PlayerOption.option_key == option_key,
            )
        )
        opt = result.scalar_one_or_none()
        if opt:
            opt.value_num = value_num
        else:
            opt = PlayerOption(player_id=player_id, option_key=option_key, value_num=value_num)
            self.session.add(opt)
        await self.session.flush()
        return opt

    async def get_missions(self, player_id: int) -> list[PlayerMission]:
        result = await self.session.execute(
            select(PlayerMission).where(PlayerMission.player_id == player_id)
        )
        return list(result.scalars().all())

    async def upsert_mission(
        self,
        player_id: int,
        mission_id: int,
        clear_count: int = 0,
        clear_num: int = 0,
        status: int = 0,
        mission_status: int = 0,
    ) -> PlayerMission:
        result = await self.session.execute(
            select(PlayerMission).where(
                PlayerMission.player_id == player_id,
                PlayerMission.mission_id == mission_id,
            )
        )
        mission = result.scalar_one_or_none()
        if mission:
            mission.clear_count = clear_count
            mission.clear_num = clear_num
            mission.status = status
            mission.mission_status = mission_status
        else:
            mission = PlayerMission(
                player_id=player_id,
                mission_id=mission_id,
                clear_count=clear_count,
                clear_num=clear_num,
                status=status,
                mission_status=mission_status,
            )
            self.session.add(mission)
        await self.session.flush()
        return mission

    async def get_titles(self, player_id: int) -> list[PlayerTitle]:
        result = await self.session.execute(
            select(PlayerTitle).where(PlayerTitle.player_id == player_id)
        )
        return list(result.scalars().all())

    async def upsert_title(self, player_id: int, title_id: int, status: int = 0) -> PlayerTitle:
        result = await self.session.execute(
            select(PlayerTitle).where(
                PlayerTitle.player_id == player_id,
                PlayerTitle.title_id == title_id,
            )
        )
        title = result.scalar_one_or_none()
        if title:
            title.status = status
        else:
            title = PlayerTitle(player_id=player_id, title_id=title_id, status=status)
            self.session.add(title)
        await self.session.flush()
        return title

    async def get_emblems(self, player_id: int) -> list[PlayerEmblem]:
        result = await self.session.execute(
            select(PlayerEmblem).where(PlayerEmblem.player_id == player_id)
        )
        return list(result.scalars().all())

    async def get_emblem_parts(self, player_id: int) -> list[PlayerEmblemPart]:
        result = await self.session.execute(
            select(PlayerEmblemPart).where(PlayerEmblemPart.player_id == player_id)
        )
        return list(result.scalars().all())

    async def upsert_emblem_part(
        self, player_id: int, part_id: int, status: int = 0
    ) -> PlayerEmblemPart:
        result = await self.session.execute(
            select(PlayerEmblemPart).where(
                PlayerEmblemPart.player_id == player_id,
                PlayerEmblemPart.part_id == part_id,
            )
        )
        part = result.scalar_one_or_none()
        if part:
            part.status = status
        else:
            part = PlayerEmblemPart(player_id=player_id, part_id=part_id, status=status)
            self.session.add(part)
        await self.session.flush()
        return part

    async def get_line_colors(self, player_id: int) -> list[PlayerLineColor]:
        result = await self.session.execute(
            select(PlayerLineColor).where(PlayerLineColor.player_id == player_id)
        )
        return list(result.scalars().all())

    async def upsert_line_color(
        self, player_id: int, line_color_id: int, status: int = 0
    ) -> PlayerLineColor:
        result = await self.session.execute(
            select(PlayerLineColor).where(
                PlayerLineColor.player_id == player_id,
                PlayerLineColor.line_color_id == line_color_id,
            )
        )
        lc = result.scalar_one_or_none()
        if lc:
            lc.status = status
        else:
            lc = PlayerLineColor(player_id=player_id, line_color_id=line_color_id, status=status)
            self.session.add(lc)
        await self.session.flush()
        return lc

    async def get_mecha_colors(self, player_id: int) -> list[PlayerMechaColor]:
        result = await self.session.execute(
            select(PlayerMechaColor).where(PlayerMechaColor.player_id == player_id)
        )
        return list(result.scalars().all())

    async def upsert_mecha_color(
        self, player_id: int, mecha_color_id: int, status: int = 0
    ) -> PlayerMechaColor:
        result = await self.session.execute(
            select(PlayerMechaColor).where(
                PlayerMechaColor.player_id == player_id,
                PlayerMechaColor.mecha_color_id == mecha_color_id,
            )
        )
        mc = result.scalar_one_or_none()
        if mc:
            mc.status = status
        else:
            mc = PlayerMechaColor(player_id=player_id, mecha_color_id=mecha_color_id, status=status)
            self.session.add(mc)
        await self.session.flush()
        return mc

    async def get_mecha_sets(self, player_id: int) -> list[PlayerMechaSet]:
        result = await self.session.execute(
            select(PlayerMechaSet).where(PlayerMechaSet.player_id == player_id)
        )
        return list(result.scalars().all())

    async def get_mecha_set_parts(
        self, player_id: int, mecha_set_id: int
    ) -> list[PlayerMechaSetPart]:
        result = await self.session.execute(
            select(PlayerMechaSetPart).where(
                PlayerMechaSetPart.player_id == player_id,
                PlayerMechaSetPart.mecha_set_id == mecha_set_id,
            )
        )
        return list(result.scalars().all())

    async def upsert_mecha_set_part(
        self,
        player_id: int,
        mecha_set_id: int,
        part_id: int,
        mecha_id: int,
        design_id: int = 0,
        color_id: int = 0,
    ) -> PlayerMechaSetPart:
        result = await self.session.execute(
            select(PlayerMechaSetPart).where(
                PlayerMechaSetPart.player_id == player_id,
                PlayerMechaSetPart.mecha_set_id == mecha_set_id,
                PlayerMechaSetPart.part_id == part_id,
            )
        )
        msp = result.scalar_one_or_none()
        if msp:
            msp.mecha_id = mecha_id
            msp.design_id = design_id
            msp.color_id = color_id
        else:
            msp = PlayerMechaSetPart(
                player_id=player_id,
                mecha_set_id=mecha_set_id,
                part_id=part_id,
                mecha_id=mecha_id,
                design_id=design_id,
                color_id=color_id,
            )
            self.session.add(msp)
        await self.session.flush()
        return msp

    async def get_side_weapons(self, player_id: int) -> list[PlayerSideWeapon]:
        result = await self.session.execute(
            select(PlayerSideWeapon).where(PlayerSideWeapon.player_id == player_id)
        )
        return list(result.scalars().all())

    async def upsert_side_weapon(
        self,
        player_id: int,
        side_weapon_id: int,
        use_count: int = 0,
        use_time: int = 0,
        status: int = 0,
    ) -> PlayerSideWeapon:
        result = await self.session.execute(
            select(PlayerSideWeapon).where(
                PlayerSideWeapon.player_id == player_id,
                PlayerSideWeapon.side_weapon_id == side_weapon_id,
            )
        )
        sw = result.scalar_one_or_none()
        if sw:
            sw.use_count = use_count
            sw.use_time = use_time
            sw.status = status
        else:
            sw = PlayerSideWeapon(
                player_id=player_id,
                side_weapon_id=side_weapon_id,
                use_count=use_count,
                use_time=use_time,
                status=status,
            )
            self.session.add(sw)
        await self.session.flush()
        return sw

    async def get_weapon_sets(self, player_id: int) -> list[PlayerWeaponSet]:
        result = await self.session.execute(
            select(PlayerWeaponSet).where(PlayerWeaponSet.player_id == player_id)
        )
        return list(result.scalars().all())

    async def upsert_weapon_set(
        self,
        player_id: int,
        weapon_set_id: int,
        use_count: int = 0,
        use_time: int = 0,
        status: int = 0,
    ) -> PlayerWeaponSet:
        result = await self.session.execute(
            select(PlayerWeaponSet).where(
                PlayerWeaponSet.player_id == player_id,
                PlayerWeaponSet.weapon_set_id == weapon_set_id,
            )
        )
        ws = result.scalar_one_or_none()
        if ws:
            ws.use_count = use_count
            ws.use_time = use_time
            ws.status = status
        else:
            ws = PlayerWeaponSet(
                player_id=player_id,
                weapon_set_id=weapon_set_id,
                use_count=use_count,
                use_time=use_time,
                status=status,
            )
            self.session.add(ws)
        await self.session.flush()
        return ws

    async def get_weapon_set_slots(
        self, player_id: int, weapon_set_id: int
    ) -> list[PlayerWeaponSetSlot]:
        result = await self.session.execute(
            select(PlayerWeaponSetSlot).where(
                PlayerWeaponSetSlot.player_id == player_id,
                PlayerWeaponSetSlot.weapon_set_id == weapon_set_id,
            )
        )
        return list(result.scalars().all())

    async def upsert_weapon_set_slot(
        self,
        player_id: int,
        weapon_set_id: int,
        slot_id: int,
        weapon_id: int,
        use_count: int = 0,
        use_time: int = 0,
    ) -> PlayerWeaponSetSlot:
        result = await self.session.execute(
            select(PlayerWeaponSetSlot).where(
                PlayerWeaponSetSlot.player_id == player_id,
                PlayerWeaponSetSlot.weapon_set_id == weapon_set_id,
                PlayerWeaponSetSlot.slot_id == slot_id,
            )
        )
        wss = result.scalar_one_or_none()
        if wss:
            wss.weapon_id = weapon_id
            wss.use_count = use_count
            wss.use_time = use_time
        else:
            wss = PlayerWeaponSetSlot(
                player_id=player_id,
                weapon_set_id=weapon_set_id,
                slot_id=slot_id,
                weapon_id=weapon_id,
                use_count=use_count,
                use_time=use_time,
            )
            self.session.add(wss)
        await self.session.flush()
        return wss
