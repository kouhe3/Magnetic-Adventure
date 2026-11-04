-- OnPersistContact test level (T6.3): a dynamic screw starts inside a static
-- WoodWall, so b2 emits Persist contacts every step.  The event script counts
-- five persists and moves the marker to (99,99).
-- Replaces lvl_o14.lua in a pak copy; no lvl_info.lvl/map change.

function Create()
	Set_CameraPosition(0, 0);
	Set_CameraViewArea(28, 20.5);
	Set_BackMaterial('back_1');
	Set_VisibleHintButton(0);

	bStatic = AddStaticWall(0, -25, 0);
	bWall = AddStaticWall(0, 0, 0);
	bBall = Add_MetallScrew(grFrontRoot, 0, 0, 0, 1);
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
