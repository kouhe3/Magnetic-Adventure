-- Coverage fixture (F406): terminal bindings after Create succeeds.
-- Level_Complete is deliberately last so all earlier entry counts are recorded.

function AttachScripts()
	if cb_ready == 1 then
		Level_Complete();
	end;
end;
