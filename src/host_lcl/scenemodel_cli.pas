program scenemodel_cli;
{$mode objfpc}{$H+}
// 场景模型 CLI（T6.4a-r-2d）：绑定 JSONL → 图元 JSONL，供与 Python 模型对拍。
// 构建（FPC 2.2.4；-FE/-FU 要连写）:
//   fpc -Mobjfpc -O1 -g- -Fu src/host_lcl -FEbuild/scene_model \
//       -FUbuild/scene_model/units src/host_lcl/scenemodel_cli.pas
// 用法：scenemodel_cli <in.jsonl> <pak_dir> <out.jsonl>
// 判据：与 `python tools/scene_from_lua.py --dump-objects` 的产物逐对象一致
// （tools/scenemodel_ab.py；跨关 dump 作负例）。
uses
  SysUtils, SceneModel;

var
  M: TSceneModel;
  i: Integer;
  O: TSceneObj;
begin
  DecimalSeparator := '.';
  if ParamCount < 3 then
  begin
    WriteLn('usage: scenemodel_cli <in.jsonl> <pak_dir> <out.jsonl> [time]');
    Halt(2);
  end;
  M := TSceneModel.Create;
  try
    if not M.BuildFromJsonl(ParamStr(1), ParamStr(2)) then
    begin
      WriteLn(StdErr, 'build failed: ', ParamStr(1));
      Halt(3);
    end;
    if ParamCount >= 4 then
      M.ApplyTime(StrToFloat(ParamStr(4)));
    for i := 0 to M.Count - 1 do
    begin
      O := M.ObjectAt(i);
      if O.HasSpeed then
        WriteLn(StdErr, 'gear ', O.Asset, ' w=', FloatToStrF(O.Speed, ffFixed, 9, 4));
    end;
    if not M.SaveJsonl(ParamStr(3)) then
    begin
      WriteLn(StdErr, 'save failed: ', ParamStr(3));
      Halt(4);
    end;
    WriteLn('objects=', M.Count, ' camera=', FloatToStrF(M.CamX, ffFixed, 9, 3),
      ',', FloatToStrF(M.CamY, ffFixed, 9, 3));
  finally
    M.Free;
  end;
end.
