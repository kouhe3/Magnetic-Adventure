-- OnClick test level events (T6.3).

function AttachScripts()
	Attach_ScriptToObject(btn, 'OnClick', 'btnOnClick');
end;

function btnOnClick()
	Set_ScrObjPos(bMarker, 99, 99, 0);
end;
