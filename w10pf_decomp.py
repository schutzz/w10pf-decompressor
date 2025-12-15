import sys
import struct
import ctypes

def decompress_pf(input_path, output_path):
    # 1. ファイルをバイナリモードで読み込む
    try:
        with open(input_path, 'rb') as f:
            header = f.read(8) # 先頭8バイトだけ読んでチェック
            if header[:4] != b'MAM\x04':
                print(f"[!] エラー: これは圧縮されたPrefetch(MAM)ではありません。ヘッダ: {header[:4]}")
                return
            
            # 展開後のサイズを取得 (Offset 0x04から4バイト)
            decompressed_size = struct.unpack('<I', header[4:8])[0]
            
            # 残りの圧縮データを全部読む
            compressed_data = f.read()
            
    except FileNotFoundError:
        print("[!] ファイルが見つかりません。パスを確認してね。")
        return

    print(f"[*] ターゲット確認: MAM形式")
    print(f"[*] 展開後の予定サイズ: {decompressed_size} bytes")

    # 2. Windows API (ntdll) を準備
    try:
        ntdll = ctypes.WinDLL('ntdll')
    except OSError:
        print("[!] エラー: ntdll.dllが見つかりません（Windows以外で実行してる？）")
        return

    # 3. Workspaceのサイズを取得
    workspace_size = ctypes.c_ulong(0)
    fragment_workspace_size = ctypes.c_ulong(0)
    
    # 0x0004 = XPRESS_HUFF
    status = ntdll.RtlGetCompressionWorkSpaceSize(
        0x0004,
        ctypes.byref(workspace_size),
        ctypes.byref(fragment_workspace_size)
    )
    
    if status != 0:
        print(f"[!] Workspaceサイズの取得に失敗: {hex(status)}")
        return

    # Workspaceを確保
    workspace = ctypes.create_string_buffer(workspace_size.value)

    # 4. メモリバッファを確保
    output_buffer = ctypes.create_string_buffer(decompressed_size)
    final_size = ctypes.c_ulong(0)
    
    # 5. 解凍実行！ (CompressionFormat 0x0004 = XPRESS_HUFF)
    # NTSTATUS RtlDecompressBufferEx(...)
    status = ntdll.RtlDecompressBufferEx(
        0x0004,                 # Format
        output_buffer,          # Destination
        decompressed_size,      # Dest Size
        compressed_data,        # Source
        len(compressed_data),   # Source Size
        ctypes.byref(final_size), # Result Size
        workspace               # Workspace
    )

    if status == 0:
        # 6. 結果をファイルに書き出し
        with open(output_path, 'wb') as f:
            f.write(output_buffer.raw)
        print(f"[+] 成功！ 解凍されたファイルを保存しました: \n    -> {output_path}")
        print(f"[+] 先頭を確認してみて！ 'SCCA' になってるはずだよ。")
    else:
        print(f"[!] 解凍失敗... NTSTATUS: {hex(status)}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("使い方: python my_decompress.py <入力ファイル.pf> <出力ファイル.pf>")
    else:
        decompress_pf(sys.argv[1], sys.argv[2])