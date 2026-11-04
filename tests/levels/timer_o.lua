-- Timer/OnTimer test level (T6.3): a simple timer fires after 1.5 s and moves
-- the marker screw to (99,99); the b2 log's SetXForm step is the criterion.
-- Replaces lvl_o14.lua in a pak copy; no lvl_info.lvl/map change.

function Create()
	Set_CameraPosition(0, 0);
	Set_CameraViewArea(28, 20.5);
	Set_BackMaterial('back_1');
	Set_VisibleHintButton(0);

	bStatic = AddStaticWall(0, -25, 0);
	bMarker = Add_MetallScrew(grFrontRoot, 10, 10, 0, 1);

	tTimer = Add_SimpleTimer();
	Start_Timer(tTimer, 1.5);

	done = 0;
	Set_GlobalVar('bMarker', bMarker);
end;

function OnResizeForm()
end;

function Destroy()
end;
