# Windows 10/11 Prefetch Decompressor

A standalone, dependency-free Python script to decompress Windows 10/11 Prefetch files (MAM format) into raw SCCA format for analysis.

## 🧐 Why this tool?

Modern Windows Prefetch files are compressed using XPRESS Huffman algorithms. While many forensic suites handle this, sometimes you need a **small, sharp tool** to:

- Decompress a single file quickly for Hex analysis.
- Understand the physical structure without abstraction layers.
- Run in a restricted environment with standard Python 3 libraries only.

## 🚀 Features

- **Dependency Free**: Uses `ctypes` to call Windows Native API (`ntdll.dll`). No `pip install` required.
- **Correct Memory Management**: Dynamically allocates workspace memory using `RtlGetCompressionWorkSpaceSize`, ensuring stability.
- **Verification Included**: Comes with a verification script to validate decompression integrity.

## 🛠️ Usage

### Decompress a file

```bash
python w10pf_decomp.py <input.pf> <output.pf>
```

**Example:**

```bash
python w10pf_decomp.py CMD.EXE-12345678.pf decompressed_cmd.pf
```

### Check generated file

The output file should start with the `SCCA` signature (Magic Header: `53 43 43 41`) and can be analyzed with any Hex Editor.

## ⚠️ Disclaimer

This tool uses `ctypes` to interact with low-level Windows APIs. Use at your own risk.
Developed for educational and forensic research purposes.

## 📜 License

MIT License
