-- Minimal test level (F387): one free metal screw at (0,0), chalk goal at (5,0).
-- Replaces lvl_o14.lua in work/pak_test_game/data; the level record still points
-- to lvl_o14.lua + lvl_e14.lua, so no lvl_info.lvl/map change is needed.

function Create()
	Set_CameraPosition(0, 0);
	Set_CameraViewArea(28, 20.5);
	Set_BackMaterial('back_1');
	Set_VisibleHintButton(0);

	Add_LevelMaterial('chscrew2.png', 'level_chalk_1');

	bScrew = Add_MetallScrew(grFrontRoot, 0, 0, 0.49, 1);
	Set_PhysParams(bScrew, 0.2, 0, 0);

	bChalkScrew = Add_AlphaHint(grMediumRoot, 5, 0, 1.75, 1.7, 1.7, 'level_chalk_1');
	Do_Command(bChalkScrew, 23, 1, 1);

	Set_GlobalVar('bScrew', bScrew);
	Set_GlobalVar('bChalkScrew', bChalkScrew);
	completed = 0;
end;

function OnResizeForm()
end;

function Destroy()
	Clear_LevelMaterial('level_chalk_1');
end;
