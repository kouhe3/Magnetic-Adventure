-- OnPersistContact negative control events (T6.3): same callback, no contact.

function AttachScripts()
	Attach_ScriptToObject(bWall, 'OnPersistContact', 'bWallPersist');
end;

function bWallPersist(Body1, Body2)
	count = count + 1;
	if count == 5 then
		Set_ScrObjPos(bMarker, 99, 99, 0);
	end;
end;
