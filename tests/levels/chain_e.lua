-- Runtime-generation test level events (T6.4b-x).
-- Stage 0: drag bScrew to bChalk1 (3,0); radius 0.6 (the magnet converges
-- to ~0.55 of the b2 origin, so 0.3 would sit on a knife edge).
-- Callback: create bScrew2 (-3,3) + bChalk2 (0,6) while the level is running
--           and register OnMove for the new body.  The first screw is left in
--           place; the harness excludes it from later stage matching by ptr.
-- Stage 1: drag bScrew2 to bChalk2, then write the (99,99) completion marker.

function AttachScripts()
	Attach_ScriptToObject(bScrew, 'OnMove', 'bScrewOnMove');
end;

function bScrewOnMove(PosX, PosY)
	if stage ~= 0 then
		return;
	end;
	local x, y, angle = Get_ScrObjPos(bChalk1);
	local len = (PosX - x) * (PosX - x) + (PosY - y) * (PosY - y);
	if len < 0.36 then
		stage = 1;
		bScrew2 = Add_MetallScrew(grFrontRoot, -3, 3, 0, 1);
		bChalk2 = Add_AlphaHint(grMediumRoot, 0, 6, 0, 1.7, 1.7, 'level_chalk_2');
		Do_Command(bChalk2, 23, 1, 1);
		Attach_ScriptToObject(bScrew2, 'OnMove', 'bScrew2OnMove');
		Set_GlobalVar('bScrew2', bScrew2);
		Set_GlobalVar('bChalk2', bChalk2);
		Do_Command(bChalk1, 23, 1, 1);
	end;
end;

function bScrew2OnMove(PosX, PosY)
	if stage ~= 1 then
		return;
	end;
	local x, y, angle = Get_ScrObjPos(bChalk2);
	local len = (PosX - x) * (PosX - x) + (PosY - y) * (PosY - y);
	if len < 0.36 then
		stage = 2;
		Set_ScrObjPos(bScrew2, 99, 99, 0);
		DoLevelComplete();
	end;
end;
