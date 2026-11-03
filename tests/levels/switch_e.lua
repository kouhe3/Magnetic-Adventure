-- Switch/OnRotate test level events (T6.4b-x).
-- OnRotate fires as the magnet drags the pinned arm; latch once and write the
-- (99,99) marker used by tools/ci_fake_magnet.py.

function AttachScripts()
	Attach_ScriptToObject(bSwitch, 'OnRotate', 'bSwitchOnRotate');
end;

function bSwitchOnRotate(Rotation)
	if done ~= 0 then
		return;
	end;
	local ang = Get_JointAngle(jSwitch);
	if math.abs(ang) > 0.2 then
		done = 1;
		Set_ScrObjPos(bMarker, 99, 99, 0);
	end;
end;
