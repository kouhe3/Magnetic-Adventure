unit FrameShot;
{$mode objfpc}{$H+}
// 直接从 GL 前缓冲/后缓冲读像素写 BMP（不经屏幕抓图）。
//
// 为什么需要：`tools/shot_window.py` 抓的是屏幕像素，窗口被别的进程盖住时会把别人的
// 像素拍进来（本仓库踩过：底部 108 px 是前台终端，被误判成渲染回归）。M6 的像素验收
// 要能重放、要与窗口层叠无关，所以宿主自己 dump。
//
// 用法（宿主侧）：HOST_DUMP_FRAME=<path.bmp> 时渲染一帧后写文件。
// 输出：24 位 BMP，**自下而上**（BMP 原生顺序），尺寸 = 当前 glViewport。
// 覆盖边界：只抓颜色缓冲，不含 alpha/深度；窗口最小化或无上下文时读回全 0。

interface

uses Windows, OpenGL1x, SysUtils;

function DumpFramebufferBmp(const Path: string; w, h: Integer): Boolean;

implementation

function DumpFramebufferBmp(const Path: string; w, h: Integer): Boolean;
var
  y, padbytes, stride: Integer;
  fsize, isize, offbits, hdrsz: Cardinal;
  i, x: Integer;
  t: Byte;
  pixels: PByte;
  bmp: array[0..53] of Byte;
  f: THandle;
  written: DWORD;
  src: PByte;
  pad: array[0..3] of Byte;
begin
  Result := False;
  if (w <= 0) or (h <= 0) then Exit;
  stride := w * 3;
  padbytes := (4 - (stride mod 4)) mod 4;   // BMP 每行 4 字节对齐
  GetMem(pixels, stride * h);
  try
    glPixelStorei(GL_PACK_ALIGNMENT, 1);
    glReadBuffer(GL_BACK);
    glReadPixels(0, 0, w, h, GL_RGB, GL_UNSIGNED_BYTE, pixels);
    // glReadPixels 给 RGB，BMP 要 BGR：就地换 R/B。
    for y := 0 to h - 1 do
    begin
      i := y * stride;
      for x := 0 to w - 1 do
      begin
        t := pixels[i];
        pixels[i] := pixels[i + 2];
        pixels[i + 2] := t;
        Inc(i, 3);
      end;
    end;
    FillChar(bmp, SizeOf(bmp), 0);
    bmp[0] := Ord('B');
    bmp[1] := Ord('M');
    isize := (stride + padbytes) * h;
    fsize := 54 + isize;
    offbits := 54;
    hdrsz := 40;
    Move(fsize, bmp[2], 4);
    Move(offbits, bmp[10], 4);
    Move(hdrsz, bmp[14], 4);
    Move(w, bmp[18], 4);
    Move(h, bmp[22], 4);
    bmp[26] := 1;
    bmp[28] := 24;
    Move(isize, bmp[34], 4);
    f := CreateFile(PChar(Path), GENERIC_WRITE, 0, nil, CREATE_ALWAYS,
      FILE_ATTRIBUTE_NORMAL, 0);
    if f = INVALID_HANDLE_VALUE then Exit;
    try
      WriteFile(f, bmp[0], 54, written, nil);
      // glReadPixels 自下而上 == BMP 的行序，直接逐行写。
      FillChar(pad, SizeOf(pad), 0);
      for y := 0 to h - 1 do
      begin
        src := pixels + y * stride;
        WriteFile(f, src^, stride, written, nil);
        if padbytes > 0 then
          WriteFile(f, pad[0], padbytes, written, nil);
      end;
      Result := True;
    finally
      CloseHandle(f);
    end;
  finally
    FreeMem(pixels);
  end;
end;

end.
