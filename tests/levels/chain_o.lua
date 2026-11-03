-- Runtime-generation test level (T6.4b-x): first screw at (0,0), chalk at (3,0).
-- The OnMove callback in chain_e.lua creates the second screw (-3,3) and its
-- chalk (0,6) at runtime, so the CI magnet must find a body that did not exist
-- when the level was built.
-- Replaces lvl_o14.lua in a pak copy; no lvl_info.lvl/map change.

function Create()
	Set_CameraPosition(0, 0);
	Set_CameraViewArea(28, 20.5);
	Set_BackMaterial('back_1');
	Set_VisibleHintButton(0);

	Add_LevelMaterial('chscrew2.png', 'level_chalk_1');
	Add_LevelMaterial('chgear_2.png', 'level_chalk_2');

	bScrew = Add_MetallScrew(grFrontRoot, 0, 0, 0, 1);
	bChalk1 = Add_AlphaHint(grMediumRoot, 3, 0, 0, 1.7, 1.7, 'level_chalk_1');
	Do_Command(bChalk1, 23, 1, 1);

	bScrew2 = 0;
	bChalk2 = 0;
	stage = 0;
	Set_GlobalVar('bScrew', bScrew);
	Set_GlobalVar('bChalk1', bChalk1);
	Set_GlobalVar('bScrew2', bScrew2);
	Set_GlobalVar('bChalk2', bChalk2);
end;

function OnResizeForm()
end;

function Destroy()
	Clear_LevelMaterial('level_chalk_1');
	Clear_LevelMaterial('level_chalk_2');
end;
