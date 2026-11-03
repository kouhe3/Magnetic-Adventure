-- Terminal coverage fixture (F406): Set_VisibleRollMap throws after entry.
-- Run alone; the entry count is recorded before the exception aborts level load.

function Create()
	Set_CameraPosition(0, 0);
	Set_BackMaterial('back_1');
	Set_VisibleRollMap(0);
end;

function OnResizeForm()
end;

function Destroy()
end;
