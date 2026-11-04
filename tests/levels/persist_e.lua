-- OnPersistContact test level events (T6.3).
-- The engine fires OnPersistContact(Body1, Body2) every step the contact
-- persists; after five events the marker moves to (99,99).

function AttachScripts()
	Attach_ScriptToObject(bWall, 'OnPersistContact', 'bWallPersist');
end;

function bWallPersist(Body1, Body2)
	count = count + 1;
	if count == 5 then
		Set_ScrObjPos(bMarker, 99, 99, 0);
	end;
end;
