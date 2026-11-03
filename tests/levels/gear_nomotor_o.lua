-- Negative fixture: motor torque is 0, so both gears must stay still.
-- Gear-torque test level (T6.4b-x): two metal gears pinned with Add_JointNail,
-- linked by Add_JointSimpleGear(ratio 0.8), motor on gear 1 at 1.0 rad/s.
-- Expected (F368): w2 = -w1/ratio = -1.25 rad/s.
-- Replaces lvl_o14.lua in a pak copy; no lvl_info.lvl/map change.

function Create()
	Set_CameraPosition(0, 0);
	Set_CameraViewArea(28, 20.5);
	Set_BackMaterial('back_1');
	Set_VisibleHintButton(0);

	-- Joint anchors need a valid static body; levels set bStatic in Create
	-- (lvl_o1/lvl_o11).  Place it outside the play area.
	bStatic = AddStaticWall(0, -25, 0);

	bGear1 = Add_MetallGear(grFrontRoot, 0, 0, 0, 1);
	bGear2 = Add_MetallGear(grFrontRoot, 5, 0, 0, 1);

	jGear1 = Add_JointNail(0, bStatic, bGear1, 0, 0);
	jGear2 = Add_JointNail(0, bStatic, bGear2, 5, 0);
	jGear = Add_JointSimpleGear(bGear1, bGear2, jGear1, jGear2, 0.8);

	Set_JointMotors(jGear1, 1, 1.0, 0);

	Set_GlobalVar('bGear1', bGear1);
	Set_GlobalVar('bGear2', bGear2);
end;

function OnResizeForm()
end;

function Destroy()
end;
