-- Runtime-spawn fixture (F447): screw (0,0) -> chalk (3,0); OnMove spawns a gear.
function Create()
	Set_CameraPosition(0, 0);
	Set_CameraViewArea(28, 20.5);
	Set_BackMaterial('back_1');
	Set_VisibleHintButton(0);

	Add_LevelMaterial('chscrew2.png', 'level_chalk_1');

	bScrew = Add_MetallScrew(grFrontRoot, 0, 0, 0, 1);
	bChalk = Add_AlphaHint(grMediumRoot, 3, 0, 1.75, 1.7, 1.7, 'level_chalk_1');
	Do_Command(bChalk, 23, 1, 1);

	Set_GlobalVar('bScrew', bScrew);
	Set_GlobalVar('bChalk', bChalk);
	spawned = 0;
end;

function OnResizeForm()
end;

function Destroy()
end;
