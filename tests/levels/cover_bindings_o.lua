-- Coverage fixture (F406): call the 73 uncovered Lua bindings in one level.
-- Replaces lvl_o14.lua in work/cover_game/data; pairs with cover_bindings_e.lua.
-- Objects are created first; every call uses a valid body/joint where one exists.

function cb_trace(s)
	if io then
		local f = io.open('cover_trace.txt', 'a');
		if f then
			f:write(s .. '\n');
			f:close();
		end;
	end;
end;

function Create()
	cb_trace('create:start');
	Set_CameraPosition(0, 0);
	Set_CameraViewArea(28, 20.5);
	Set_BackMaterial('back_1');
	Set_VisibleHintButton(0);
	cb_trace('before Set_HideTimeHint');
	Set_HideTimeHint(20);
	cb_trace('after Set_HideTimeHint');
	Set_DebugPosition(5, 0);
	Set_DebugText('cover_bindings');
	Drop_ToLog('cover_bindings');
	Get_MousePosition();
	Get_PhysicTime();
	Set_CameraRotation(0.1);
	cb_trace('camera done');

	Add_LevelMaterial('hint_1.png', 'lvl_hint_1');
	Add_LevelMaterial('hint_2.png', 'lvl_hint_2');
	Add_LevelMaterial('chscrew2.png', 'level_chalk_1');
	Add_LevelMaterial('chgear_2.png', 'level_chalk_2');
	cb_trace('materials done');

	cb_static = Add_SimplePhysicObject(0, 0, 0);
	Attach_ShapeCircle(cb_static, 0.1, 0.1, 0, 0, 0, 1.0);
	Set_PhysParams(cb_static, 0, 0.1, 0.1);
	cb_trace('static done');

	cb_box1 = Add_WoodBox(grFrontRoot, -2, 0, 0, 1);
	cb_box2 = Add_WoodBox(grFrontRoot, 2, 0, 0, 1);
	cb_gear = Add_MetallGear(grFrontRoot, 3, 0, 0, 1);
	cb_screw = Add_MetallScrew(grFrontRoot, -3, 0, 0, 1);
	cb_doomed = Add_WoodBox(grFrontRoot, 6, 0, 0, 1);
	cb_gr = Add_GraphSprite(grFrontRoot, 0, 4, 0, 2, 2, 'lvl_hint_1');
	cb_gr2 = Add_SpringSprite(grMediumRoot, 0, -4, 0, 1, 2);
	cb_rope = Add_Rope(grFrontRoot, 0, 0, 0, 0.2, 0.2, 0.4, 0.4);
	cb_trace('bodies done');

	Add_HammerParts(grFrontRoot, -6, 4, 0, 1);
	Add_Ball(grFrontRoot, -6, 2, 0, 1);
	Add_ControlArm(grFrontRoot, -6, 0, 0, 1);
	Add_ScrewDriver(grFrontRoot, -6, -2, 0, 1);
	Add_Cork(grFrontRoot, -6, -4, 0, 1);
	Add_TestTube(grFrontRoot, -6, -6, 0, 1);
	Add_Lamp(grMediumRoot, 6, 4, 0, 4);
	Add_Magnet(grFrontRoot, 6, 2, 0, 1);
	Add_WoodDetail(grFrontRoot, 6, 0, 0, 1);
	Add_ToothGear(grMediumRoot, 6, -2, 0, 1);
	Add_ShankBody(grBackRoot, 6, -4, 0, 1);
	Add_SpiderWeb(grFrontRoot, 8, 0, 0, 1);
	Add_WoodFormWall(grBackRoot, -8, 0, 0, 1);
	Add_WoodFormWall(grBackRoot, -8, 2, 0, 2);
	Add_WoodFormWall(grBackRoot, -8, 4, 0, 3);
	Add_Rack(grFrontRoot, -8, 2, 0, 1);
	Add_PhysicObjectWithAdvGraph(-8, 4, 0, 177/256*9, 0);
	Add_Symbol(grFrontRoot, -10, 0, 0, 1);
	Add_DoorHandle(grFrontRoot, -10, 2, 0, 1);
	Add_Battery(grFrontRoot, -10, 4, 0, 1);
	Add_ElectricPlug(grFrontRoot, -10, 6, 0, 1);
	Add_Spanner(grFrontRoot, -10, -2, 0, 1);
	Add_StaticCan(grFrontRoot, -10, -4, 0, 1);
	Add_PropellerFan(grFrontRoot, -10, -6, 0, 1);
	Add_Barrel(grFrontRoot, -10, -8, 0, 1);
	Add_GearChalkSprite(grFrontRoot, 10, 0, 0, 1);
	Add_HudGraphSprite(grFrontRoot, 0, 0, 0, 0, 0, 'lvl_hint_1');
	Add_AlphaDoubleSprite(grFrontRoot, 10, 2, 0, 2, 2, 'lvl_hint_1', 'lvl_hint_2');
	Add_ExtAlphaDoubleSprite(grFrontRoot, 10, 4, 0, 2, 2, 4, 4, 'lvl_hint_1', 'lvl_hint_2');
	Add_MovingPipe(grBackRoot, 0, 0, 0, 1);
	Add_SimpleButton(0, 0, 0, 0, 4, 2, 'btn_restart_2', 'btn_restart_1');
	cb_trace('factories done');

	cb_j_nail = Add_JointNail(0, cb_static, cb_box1, -2, 0);
	cb_j_skid = Add_JointSkid(0, cb_static, cb_box2, 2, 0, -1, 0);
	cb_j_dist = Add_JointDistance(0, cb_box1, cb_box2, -2, 0, 2, 0, 1);
	cb_j_nailstatic = Add_JointNailToStatic(0, cb_static, cb_box2, 2);
	cb_j_pulley = Add_JointSimplePulley(cb_box1, cb_box2, -2, 0, 2, 0, 0, 1, 0, 1, 1, 1, 1);
	cb_trace('joints done');

	Get_JointLimits(cb_j_nail);
	Get_PhysVelocity(cb_box1);
	Get_PhysObjByIndex(0);
	Get_GraphObject(cb_gear);
	Get_RopeJointItem(cb_rope, 0);
	Get_RopePhysItem(cb_rope, 0);
	Get_JointReactionForce(cb_j_nail);
	Set_JointThresholdForce(cb_j_nail, 0, 0, 1);
	cb_trace('getters done');

	Set_PhysBullet(cb_box1, 1);
	Set_PhysThresholdPlayerForce(cb_box2, 300);
	Set_PhysVelocity(cb_box1, 0.1, 0);
	Apply_PhysImpulse(cb_box1, 0.1, 0.1);
	Apply_PhysForceAtPos(cb_box1, 0.1, 0.1, 0, 0);
	cb_trace('phys done');

	Flip_GraphObjectX(cb_gr);
	Flip_GraphObjectY(cb_gr);
	Set_FlipGraphObject(cb_gr, 0, 1);
	Set_GraphObjectParent(cb_gr, grFrontRoot);
	Set_GraphMaterial(cb_gr, 'lvl_hint_1', 'lvl_hint_2');
	Attach_AlphaHintGraphObject(cb_box1, grBackRoot, 1, 1, 'lvl_hint_1', 'lvl_hint_2');
	Attach_AlphaHintExGraphObject(cb_box2, grFrontRoot, 1, 1, 2, 2, 'lvl_hint_1', 'lvl_hint_2');
	Set_MaterialEmission('lvl_hint_1', 0.3, 0.1, 0.2);
	Local_ToWorld(cb_gear, 0, 0);
	World_ToLocal(cb_gear, 0, 0);
	cb_trace('graph done');

	-- Add_LevelSound is covered by cover_bindings_terminal_o.lua (it throws after entry).
	cb_trace('before Start_MusicSample');
	Start_MusicSample('track2');
	cb_trace('after Start_MusicSample');
	cb_trace('before Play_LoopSoundSample');
	Play_LoopSoundSample('track2');
	cb_trace('after Play_LoopSoundSample');
	Pause_SoundSample('track2', 1);
	Stop_SoundSample('track2');
	Pause_AllMusic(1);
	Stop_AllMusic();
	cb_trace('sound done');

	Destroy_Body(cb_doomed);
	Set_GlobalVar('cb_ready', 1);
	cb_trace('create done');
end;

function OnResizeForm()
end;

function Destroy()
	Clear_LevelMaterial('lvl_hint_1');
	Clear_LevelMaterial('lvl_hint_2');
	Clear_LevelMaterial('level_chalk_1');
	Clear_LevelMaterial('level_chalk_2');
end;
