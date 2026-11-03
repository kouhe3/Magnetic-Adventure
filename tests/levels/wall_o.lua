-- Obstacle test level (T6.4b-x): free metal screw (0,0), chalk goal (9,0), and a
-- static barrier at x≈2.2..5.4 (three overlapping WoodFormWall style-4 segments,
-- each x∈[-0.84,0.81], y∈[-3.31,3.38]).
-- The density is raised so the magnet cannot tunnel the 3.2-unit-thick barrier;
-- a straight drag stops at the wall, a waypoint route over y=6 reaches the goal.
-- Replaces lvl_o14.lua in a pak copy; no lvl_info.lvl/map change.

function Create()
	Set_CameraPosition(0, 0);
	Set_CameraViewArea(28, 20.5);
	Set_BackMaterial('back_1');
	Set_VisibleHintButton(0);

	Add_LevelMaterial('chscrew2.png', 'level_chalk_1');

	bScrew = Add_MetallScrew(grFrontRoot, 0, 0, 0, 1);
	Set_PhysParams(bScrew, 5.0, 0, 0);

	bChalk = Add_AlphaHint(grMediumRoot, 9, 0, 0, 1.7, 1.7, 'level_chalk_1');
	Do_Command(bChalk, 23, 1, 1);

	local w1 = Add_WoodFormWall(grBackRoot, 3.0, 0, 0, 4); SetStaticMass(w1);
	local w2 = Add_WoodFormWall(grBackRoot, 3.8, 0, 0, 4); SetStaticMass(w2);
	local w3 = Add_WoodFormWall(grBackRoot, 4.6, 0, 0, 4); SetStaticMass(w3);

	done = 0;
	Set_GlobalVar('bScrew', bScrew);
	Set_GlobalVar('bChalk', bChalk);
end;

function OnResizeForm()
end;

function Destroy()
	Clear_LevelMaterial('level_chalk_1');
end;
