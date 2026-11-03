-- Minimal test level events (F387): complete when the screw reaches the chalk.

function AttachScripts()
	Attach_ScriptToObject(bScrew, 'OnMove', 'bScrewOnMove');
end;

function bScrewOnMove(PosX, PosY)
	local x, y, angle = Get_ScrObjPos(bChalkScrew);
	local len = (PosX - x) * (PosX - x) + (PosY - y) * (PosY - y);
	if (len < 0.3) and (completed == 0) then
		completed = 1;
		Set_ScrObjPos(bScrew, 99, 99, 0);
		DoLevelComplete();
	end;
end;
