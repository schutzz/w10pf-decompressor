import ctypes
import struct
import os
import subprocess
import sys

def create_test_file(filename):
    print(f"[*] Creating test file: {filename}")
    
    # 1. Prepare data
    original_data = (b"Hello World! " * 100) + (b"Repeated Data " * 50)
    original_size = len(original_data)
    print(f"    Original size: {original_size} bytes")

    # 2. Setup Windows API
    try:
        ntdll = ctypes.WinDLL('ntdll')
    except OSError:
        print("[!] Failed to load ntdll.dll")
        return None, None

    # Constants
    COMPRESSION_FORMAT_XPRESS_HUFF = 0x0004
    
    # 3. Get Workspace Size
    workspace_size = ctypes.c_ulong(0)
    fragment_workspace_size = ctypes.c_ulong(0)
    
    status = ntdll.RtlGetCompressionWorkSpaceSize(
        COMPRESSION_FORMAT_XPRESS_HUFF,
        ctypes.byref(workspace_size),
        ctypes.byref(fragment_workspace_size)
    )
    
    if status != 0:
        print(f"[!] RtlGetCompressionWorkSpaceSize failed: {hex(status)}")
        return None, None

    # 4. Allocate Workspace
    workspace = ctypes.create_string_buffer(workspace_size.value)
    
    # 5. Compress
    # Allocate output buffer (worst case size + overhead)
    compressed_buffer_size = original_size + 4096 
    compressed_buffer = ctypes.create_string_buffer(compressed_buffer_size)
    final_compressed_size = ctypes.c_ulong(0)
    
    status = ntdll.RtlCompressBuffer(
        COMPRESSION_FORMAT_XPRESS_HUFF,
        original_data,
        original_size,
        compressed_buffer,
        compressed_buffer_size,
        4096, # Chunk size (standard 4KB)
        ctypes.byref(final_compressed_size),
        workspace
    )
    
    if status != 0:
        print(f"[!] RtlCompressBuffer failed: {hex(status)}")
        return None, None
        
    compressed_size = final_compressed_size.value
    print(f"    Compressed size: {compressed_size} bytes")
    
    # 6. Write MAM file
    # Header: MAM\x04 + Uncompressed Size (4 bytes)
    header = b'MAM\x04' + struct.pack('<I', original_size)
    
    with open(filename, 'wb') as f:
        f.write(header)
        f.write(compressed_buffer.raw[:compressed_size])
        
    return original_data, filename

def verify_decompressor(test_file, original_data):
    output_file = test_file + ".decompressed"
    if os.path.exists(output_file):
        os.remove(output_file)
        
    print(f"[*] Running my_decompress.py on {test_file}...")
    
    # Run the script
    cmd = [sys.executable, "my_decompress.py", test_file, output_file]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print("    STDOUT:", result.stdout)
    if result.stderr:
        print("    STDERR:", result.stderr)
        
    if result.returncode != 0:
        print("[!] Script failed with return code", result.returncode)
        return False

    if not os.path.exists(output_file):
        print("[!] Output file was not created")
        return False
        
    with open(output_file, 'rb') as f:
        decompressed_data = f.read()
        
    if decompressed_data == original_data:
        print("[+] SUCCESS: Decompressed data matches original data!")
        return True
    else:
        print("[!] FAILURE: Data mismatch")
        print(f"    Expected len: {len(original_data)}, Got: {len(decompressed_data)}")
        return False

if __name__ == "__main__":
    pf_file = "test_sample.pf"
    data, path = create_test_file(pf_file)
    if data:
        verify_decompressor(path, data)
