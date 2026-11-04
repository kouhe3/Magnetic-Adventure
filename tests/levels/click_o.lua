-- OnClick test level (T6.3): an Add_HudButton placed at design (500,300).
-- The event script attaches OnClick and moves the marker to (99,99).
-- Replaces lvl_o14.lua in a pak copy; no lvl_info.lvl/map change.

function Create()
	Set_CameraPosition(0, 0);
	Set_CameraViewArea(28, 20.5);
	Set_BackMaterial('back_1');
	Set_VisibleHintButton(0);

	bStatic = AddStaticWall(0, -25, 0);
	btn = Add_HudButton(grHintsRoot, 0, 0, 0, 64, 32, 'btn_next_4', 'btn_next_3');
	Set_ScrObjPos(btn, 500, 300, 0);
	bMarker = Add_MetallScrew(grFrontRoot, 10, 10, 0, 1);

	Set_GlobalVar('btn', btn);
	Set_GlobalVar('bMarker', bMarker);
end;

function OnResizeForm()
end;

function Destroy()
end;
