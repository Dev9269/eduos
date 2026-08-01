import pytest
import json
import sys
sys.path.insert(0, '.')


def test_agent_imports():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "agent", "Services/eduos-agent.py")
    assert spec is not None


def test_get_mac_address():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "agent", "Services/eduos-agent.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    mac = module.get_mac_address()
    assert mac is not None
    assert len(mac) > 0


def test_command_ping():
    import asyncio
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "agent", "Services/eduos-agent.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = asyncio.run(module.handle_command({'action': 'ping'}))
    assert result['status'] == 'pong'


def test_command_unknown():
    import asyncio
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "agent", "Services/eduos-agent.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = asyncio.run(module.handle_command({'action': 'nope'}))
    assert result['status'] == 'unknown_command'


def test_command_get_status():
    import asyncio
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "agent", "Services/eduos-agent.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = asyncio.run(module.handle_command({'action': 'get_status'}))
    assert result['status'] == 'ok'
    assert 'hostname' in result
    assert 'platform' in result
    assert 'cpu_percent' in result
    assert 'ram_percent' in result


def test_agent_platform_detection():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "agent", "Services/eduos-agent.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert callable(module._is_freebsd)
    assert callable(module._is_linux)
    assert not (module._is_freebsd() and module._is_linux())
