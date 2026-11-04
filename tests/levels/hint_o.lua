-- Hint-button test level (T6.4f): marker object + hint button enabled.
-- Replaces lvl_o14.lua in a pak copy; the level record still points at lvl_o14.

function Create()
	Set_CameraPosition(0, 0);
	Set_CameraViewArea(28, 20.5);
	Set_BackMaterial('back_1');
	Set_VisibleHintButton(1);
	Set_HideTimeHint(5);

	Add_LevelMaterial('chscrew2.png', 'level_chalk_1');
	bMarker = Add_AlphaHint(grMediumRoot, 0, 0, 1.75, 1.7, 1.7, 'level_chalk_1');
	Set_GlobalVar('bMarker', bMarker);
end;

function OnResizeForm()
end;

function Destroy()
	Clear_LevelMaterial('level_chalk_1');
end;
