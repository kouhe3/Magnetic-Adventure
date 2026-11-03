-- Switch/OnRotate test level (T6.4b-x): a pinned switch arm at (0,0) whose
-- pivot is (0,-1.6); dragging the arm with the magnet rotates it within the
-- joint limits (-0.5..0.5).  The OnRotate callback teleports a marker screw to
-- (99,99), which tools/ci_fake_magnet.py parses from the b2 log.
-- Replaces lvl_o14.lua in a pak copy; no lvl_info.lvl/map change.

function Create()
	Set_CameraPosition(0, 0);
	Set_CameraViewArea(28, 20.5);
	Set_BackMaterial('back_1');
	Set_VisibleHintButton(0);

	bStatic = AddStaticWall(0, -25, 0);
	bSwitch, jSwitch = AddSimpleSwitchArm(0, 0, 0, 1, bStatic);
	bMarker = Add_MetallScrew(grFrontRoot, 10, 10, 0, 1);

	done = 0;
	Set_GlobalVar('bSwitch', bSwitch);
	Set_GlobalVar('jSwitch', jSwitch);
	Set_GlobalVar('bMarker', bMarker);
end;

function OnResizeForm()
end;

function Destroy()
end;
