-- Terminal coverage fixture (F406): Add_LevelSound throws after entry.
-- Run alone; the entry count is recorded before the exception aborts level load.

function Create()
	Set_CameraPosition(0, 0);
	Set_BackMaterial('back_1');
	Add_LevelSound('track2.ogg', 'track2');
end;

function OnResizeForm()
end;

function Destroy()
end;
