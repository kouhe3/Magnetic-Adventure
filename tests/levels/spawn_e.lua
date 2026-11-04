-- Runtime-spawn fixture events (F447): on reaching chalk, spawn a metal gear.
function AttachScripts()
	Attach_ScriptToObject(bScrew, 'OnMove', 'bScrewOnMove');
end;

function bScrewOnMove(PosX, PosY)
	local x, y, angle = Get_ScrObjPos(bChalk);
	local len = (PosX - x) * (PosX - x) + (PosY - y) * (PosY - y);
	if (len < 0.3) and (spawned == 0) then
		spawned = 1;
		bGear = Add_MetallGear(grFrontRoot, 0, 0, 0, 1);
		Set_GlobalVar('bGear', bGear);
	end;
end;
