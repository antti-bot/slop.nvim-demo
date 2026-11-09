"""Set up, record, verify, and render the demo in an isolated Rex session."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import uuid

ROOT = Path(__file__).resolve().parent

def main():
    plugin = Path(os.environ.get('SLOP_PLUGIN_ROOT', ROOT.parent.parent / 'slop.nvim')).resolve()
    if not (plugin / 'tests/gh').is_file():
        sys.exit('Set SLOP_PLUGIN_ROOT to a slop.nvim checkout.')
    nvim = shutil.which(os.environ.get('NVIM', 'nvim'))
    gitsigns = Path(os.environ.get('GITSIGNS_RTP', ROOT.parent.parent / 'gitsigns.nvim')).resolve()
    if not nvim or not (gitsigns / 'lua/gitsigns').is_dir():
        sys.exit('Set NVIM and GITSIGNS_RTP to Neovim 0.11+ and a Gitsigns checkout.')
    # Check rendering dependencies before opening a terminal.
    import PIL
    import imageio_ffmpeg
    if not Path(os.environ.get('DEMO_FONT', '')).is_file():
        sys.exit('Set DEMO_FONT to a monospace TTF file.')
    with tempfile.TemporaryDirectory(prefix='slop-demo-') as directory:
        work = Path(directory)
        def git(*args):
            return subprocess.check_output(['git', '-C', directory, *args], text=True).strip()
        git('init', '-q')
        git('config', 'user.name', 'Demo')
        git('config', 'user.email', 'demo@example.com')
        source = (ROOT / 'pagination.lua').read_text()
        (work / 'pagination.lua').write_text(source)
        git('add', 'pagination.lua')
        git('commit', '-qm', 'Add pagination helper')
        base = git('rev-parse', 'HEAD')
        (work / 'pagination.lua').write_text(source.replace(
            '  local first', '  page = math.max(1, page)\n  size = math.max(1, size)\n  local first'
        ).replace('"Page %d of %d"', '"%d / %d"'))
        git('commit', '-qam', 'Clamp inputs and simplify label')
        state = work / 'github.json'
        state.write_text(json.dumps({'pr': {
            'id': 'PR_demo', 'number': 42,
            'url': 'https://github.com/demo/pagination/pull/42',
            'baseRefOid': base, 'headRefOid': git('rev-parse', 'HEAD'),
        }, 'comments': []}))
        session = None
        try:
            created = json.loads(subprocess.check_output([
                'rex', 'new', 'slop-demo-' + uuid.uuid4().hex[:8], '-c', directory,
                '--json', '--shell=none', '--', 'env',
                'SLOP_DEMO_ROOT=' + str(plugin), 'GITSIGNS_RTP=' + str(gitsigns),
                'SLOP_TEST_STATE=' + str(state), nvim, '-u', str(ROOT / 'init.lua'),
                '-i', 'NONE', 'pagination.lua',
            ], text=True))
            session = created['session_id']
            env = dict(os.environ, SLOP_DEMO_SESSION=session, SLOP_TEST_STATE=str(state))
            subprocess.run([sys.executable, str(ROOT / 'record.py')], env=env, check=True)
        finally:
            if session:
                subprocess.run(['rex', 'kill', session], check=True)
    subprocess.run([sys.executable, str(ROOT / 'render.py')], check=True)

if __name__ == '__main__':
    main()
