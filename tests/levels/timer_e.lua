-- Timer/OnTimer test level events (T6.3).
-- The engine fires OnTimer once after Start_Timer(tTimer, 1.5); latch and move
-- the marker to (99,99), which both the b2 log and the host step log expose.

function AttachScripts()
	Attach_ScriptToObject(tTimer, 'OnTimer', 'tTimerOnTimer');
end;

function tTimerOnTimer()
	if done ~= 0 then
		return;
	end;
	done = 1;
	Set_ScrObjPos(bMarker, 99, 99, 0);
end;
