-- OnPersistContact negative control (T6.3): the screw is far from the wall, so
-- no Persist contact exists and the marker must stay at (10,10).

function Create()
	Set_CameraPosition(0, 0);
	Set_CameraViewArea(28, 20.5);
	Set_BackMaterial('back_1');
	Set_VisibleHintButton(0);

	bStatic = AddStaticWall(0, -25, 0);
	bWall = AddStaticWall(0, 0, 0);
	bBall = Add_MetallScrew(grFrontRoot, 15, 15, 0, 1);
	bMarker = Add_MetallScrew(grFrontRoot, 10, 10, 0, 1);

	count = 0;
	Set_GlobalVar('bWall', bWall);
	Set_GlobalVar('bBall', bBall);
	Set_GlobalVar('bMarker', bMarker);
end;

function OnResizeForm()
end;

function Destroy()
end;
