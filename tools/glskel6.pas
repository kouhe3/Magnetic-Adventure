program glskel5;
{$mode objfpc}{$H+}
uses
  Interfaces, Forms, Controls, ComCtrls, ActnList,
  GLScene, GLLCLViewer, GLObjects, GLCadencer, GLContext, GLGraphics, GLTexture,
  GLMaterial, GLFilePNG, GLHUDObjects, GLGeomObjects, GLMultiPolygon, GLBitmapFont,
  GLExtrusion, GLSilhouette, GLCoordinates, VectorLists, BaseClasses, PersistentClasses;
var F: TForm; V: TGLSceneViewer; S: TGLScene;
begin
  Application.Initialize;
  F := TForm.CreateNew(nil, 0);
  S := TGLScene.Create(F);
  V := TGLSceneViewer.Create(F);
  V.Parent := F; V.Align := alClient;
  F.Show; Application.Run;
end.
