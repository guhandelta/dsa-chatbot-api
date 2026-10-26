from pathlib import Path
import pytest

from app.core.config import settings
from app.services import container_executor as ce, code_runner


@pytest.fixture
def configured(monkeypatch):
    monkeypatch.setattr(settings, 'exec_container_image', 'local/dsa@sha256:'+'a'*64)
    monkeypatch.setattr(ce.shutil, 'which', lambda _: '/usr/bin/docker')


def test_container_has_no_host_secrets_or_network(configured, tmp_path):
    args = ce.command(['/host/jdk/bin/java', '-cp', str(tmp_path), 'Main'], tmp_path, 'dsa-test')
    assert '--network=none' in args and '--read-only' in args
    assert '--cap-drop=ALL' in args and '--security-opt=no-new-privileges' in args
    assert '--pull=never' in args and '--pids-limit' in args and '--memory-swap' in args
    assert 'core=0:0' in args
    assert args[-4:] == ['java', '-cp', '/work', 'Main']
    assert 'local/dsa@sha256:'+'a'*64 in args
    assert args[args.index('--entrypoint')+1] == 'timeout'
    assert args[args.index('--signal=KILL')+1] == f'{settings.exec_timeout_seconds}s'
    assert '--privileged' not in args
    assert not any('/.env' in a or 'API_KEY' in a or '/var/run/docker.sock' in a for a in args)


@pytest.mark.parametrize('image', ['', 'local/dsa:latest', 'local/dsa@sha256:bad'])
def test_missing_unpinned_image_fails_closed(configured, monkeypatch, tmp_path, image):
    monkeypatch.setattr(settings, 'exec_container_image', image)
    with pytest.raises(RuntimeError, match='digest-pinned'):
        ce.command(['python3', 'main.py'], tmp_path, 'name')


def test_docker_start_failure_is_infrastructure_and_cleanup_runs(configured, monkeypatch, tmp_path):
    removed = []
    monkeypatch.setattr(ce, 'cleanup', removed.append)
    with pytest.raises(RuntimeError, match='infrastructure'):
        ce.run(['python3', 'main.py'], tmp_path, '', lambda *a, **kw: (125, '', 'daemon down'))
    assert len(removed) == 1


def test_backend_dispatch_never_falls_back(configured, monkeypatch, tmp_path):
    monkeypatch.setattr(settings, 'exec_backend', 'docker')
    monkeypatch.setattr(ce, 'run', lambda *a: (_ for _ in ()).throw(RuntimeError('unavailable')))
    monkeypatch.setattr(code_runner, '_run_host', lambda *a, **kw: pytest.fail('host fallback'))
    with pytest.raises(RuntimeError, match='unavailable'):
        code_runner._run(['python3', 'main.py'], tmp_path)


def test_local_content_addressed_image_id_is_pinned(configured,monkeypatch,tmp_path):
    monkeypatch.setattr(settings,'exec_container_image','sha256:'+'b'*64)
    assert 'sha256:'+'b'*64 in ce.command(['python3','main.py'],tmp_path,'test')


def test_compiled_executable_and_source_paths_map_into_scratch(configured,tmp_path):
    executable=tmp_path/'solution'
    assert ce.command([str(executable)],tmp_path,'test')[-1]=='/work/solution'
    args=ce.command(['gcc',str(tmp_path/'solution.c'),'-o',str(executable)],tmp_path,'test')
    assert args[-3:]==['/work/solution.c','-o','/work/solution']


def test_symlink_alias_for_scratch_maps_to_same_container_path(configured,tmp_path):
    scratch=tmp_path/'real';scratch.mkdir()
    alias=tmp_path/'alias';alias.symlink_to(scratch,target_is_directory=True)
    args=ce.command(['java','-cp',str(alias),'Main'],alias,'test')
    assert args[-3:]==['-cp','/work','Main']


def test_default_backend_is_docker():
    from app.core.config import Settings
    assert Settings.model_fields['exec_backend'].default == 'docker'


@pytest.mark.parametrize('backend', ['subprocess', 'docker'])
async def test_production_startup_rejects_unsafe_configuration(monkeypatch, backend):
    from app.main import lifespan, app
    import app.main as main
    monkeypatch.setattr(settings, 'app_env', 'production')
    monkeypatch.setattr(settings, 'exec_backend', backend)
    monkeypatch.setattr(settings, 'exec_container_image', '')
    async def forbidden_db():
        pytest.fail('database startup preceded execution validation')
    monkeypatch.setattr(main, 'init_db', forbidden_db)
    with pytest.raises(RuntimeError, match='EXEC_BACKEND=docker|digest-pinned'):
        async with lifespan(app):
            pytest.fail('unsafe application started')


def test_production_execution_cannot_use_host(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, 'app_env', 'production')
    monkeypatch.setattr(settings, 'exec_backend', 'subprocess')
    monkeypatch.setattr(code_runner, '_run_host', lambda *a, **kw: pytest.fail('host execution'))
    with pytest.raises(RuntimeError, match='Production requires'):
        code_runner._run(['node', 'solution.js'], tmp_path)
