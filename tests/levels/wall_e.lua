-- Obstacle test level events (T6.4b-x).
-- Completion when the screw reaches chalk (9,0) within radius 0.6;
-- writes the (99,99) marker parsed by tools/ci_fake_magnet.py.

function AttachScripts()
	Attach_ScriptToObject(bScrew, 'OnMove', 'bScrewOnMove');
end;

function bScrewOnMove(PosX, PosY)
	if done ~= 0 then
		return;
	end;
	local x, y, angle = Get_ScrObjPos(bChalk);
	local len = (PosX - x) * (PosX - x) + (PosY - y) * (PosY - y);
	if len < 0.36 then
		done = 1;
		Set_ScrObjPos(bScrew, 99, 99, 0);
		DoLevelComplete();
	end;
end;
