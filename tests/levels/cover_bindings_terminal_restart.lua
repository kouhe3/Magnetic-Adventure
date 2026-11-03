-- Terminal coverage fixture (F406): Level_Restart once, then stop restarting.
-- Uses a file marker so a reloaded level does not restart forever.

function Create()
	Set_CameraPosition(0, 0);
	Set_BackMaterial('back_1');
	local done = false;
	if io then
		local f = io.open('cover_restart_done', 'r');
		if f then
			done = true;
			f:close();
		end;
	end;
	if not done then
		if io then
			local g = io.open('cover_restart_done', 'w');
			g:write('1');
			g:close();
		end;
		Level_Restart();
	end;
end;

function OnResizeForm()
end;

function Destroy()
end;
