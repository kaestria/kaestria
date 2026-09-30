import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from bin.appcommand.Language import compileSource
def run():
    if len(sys.argv) < 2:
        print("Usage: python Compiler.py <source.aplang> [output.AppCommand]")
        sys.exit(1)
    srcPath = Path(sys.argv[1])
    if not srcPath.exists():
        print(f"File not found: {srcPath}")
        sys.exit(1)
    outPath = Path(sys.argv[2]) if len(sys.argv) > 2 else srcPath.with_suffix(".AppCommand")
    source = srcPath.read_text(encoding="utf-8")
    hexContent = compileSource(source)
    outPath.write_text(hexContent, encoding="utf-8")
    print(f"Compiled: {outPath}")
if __name__ == "__main__":
    run()
