-- OnThresholdPlayerForce test level events (T6.3).

function AttachScripts()
	Attach_ScriptToObject(bScrew, 'OnThresholdPlayerForce', 'onForce');
end;

function onForce(fx, fy)
	if done == 0 then
		done = 1;
		Set_ScrObjPos(bMarker, 99, 99, 0);
	end;
end;
