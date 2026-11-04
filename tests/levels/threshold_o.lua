-- OnThresholdPlayerForce test level (T6.3): a free metal screw with a player
-- force threshold of 100; the event script latches and moves the marker.
-- Replaces lvl_o14.lua in a pak copy; no lvl_info.lvl/map change.

function Create()
	Set_CameraPosition(0, 0);
	Set_CameraViewArea(28, 20.5);
	Set_BackMaterial('back_1');
	Set_VisibleHintButton(0);

	bStatic = AddStaticWall(0, -25, 0);
	bScrew = Add_MetallScrew(grFrontRoot, 0, 0, 0, 1);
	Set_PhysThresholdPlayerForce(bScrew, 100);
	bMarker = Add_MetallScrew(grFrontRoot, 10, 10, 0, 1);

	done = 0;
	Set_GlobalVar('bScrew', bScrew);
	Set_GlobalVar('bMarker', bMarker);
end;

function OnResizeForm()
end;

function Destroy()
end;
