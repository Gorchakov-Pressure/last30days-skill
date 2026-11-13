"""grok as a CLI-gated dependency in the shared health layer.

The off-PATH case is confirmed real, not theoretical: on a GrokBot machine the
official installer placed the binary at ~/.grok/bin/grok and it had to be
invoked by absolute path. That is the class the Digg learning documents --
"present on disk" is not "installed".
"""

from lib import health, prescriptions


def test_grok_is_a_known_dependency():
    assert "grok" in health.KNOWN_DEPENDENCIES


def test_missing_binary_yields_an_install_prescription(monkeypatch):
    monkeypatch.setattr(health.shutil, "which", lambda name: None)
    monkeypatch.setattr(health, "_off_path_binary", lambda name: None)
    probe = health.probe_dependency("grok")
    assert probe.status == health.MISSING
    assert probe.prescription == health._prescription("grok", "install")[0]
    assert not probe.off_path
    assert "reinstall" not in probe.prescription.lower()


def test_off_path_binary_yields_a_path_edit_not_an_install(monkeypatch, tmp_path):
    binary = tmp_path / "grok"
    binary.write_text("#!/bin/sh\n")
    binary.chmod(0o755)
    monkeypatch.setattr(health.shutil, "which", lambda name: None)
    monkeypatch.setattr(health, "_off_path_binary", lambda name: binary)
    probe = health.probe_dependency("grok")
    assert probe.status == health.MISSING
    assert probe.off_path is True
    assert "PATH" in probe.prescription
    assert "install" not in probe.prescription.lower().replace("installed", "")


def test_broken_binary_yields_a_reinstall_prescription(monkeypatch):
    monkeypatch.setattr(health.shutil, "which", lambda name: "/usr/bin/grok")

    def boom(*a, **k):
        raise OSError("exec format error")

    monkeypatch.setattr(health.subproc, "run_with_timeout", boom)
    probe = health.probe_dependency("grok")
    assert probe.status == health.BROKEN
    assert probe.prescription == health._prescription("grok", "reinstall")[0]


def test_grok_install_policy_is_manual_with_or_without_npm(monkeypatch):
    for npm in (None, "/usr/bin/npm"):
        monkeypatch.setattr(health.shutil, "which", lambda name: npm if name == "npm" else None)
        for kind in ("install", "reinstall"):
            text, manager = health._prescription("grok", kind)
            assert text == health._FALLBACK_PRESCRIPTIONS["grok"][kind == "reinstall"]
            assert manager == ""
            for required in ("manually", "pinned", "operator consent", "independently verified authenticity", "stop if unverifiable"):
                assert required in text
            assert "curl" not in text and "npm" not in text


def test_timeout_keeps_manual_reinstall_policy(monkeypatch):
    monkeypatch.setattr(health.shutil, "which", lambda name: "/usr/bin/grok")

    def timeout(*args, **kwargs):
        raise health.subproc.SubprocTimeout("timeout")

    monkeypatch.setattr(health.subproc, "run_with_timeout", timeout)
    probe = health._probe_dependency_uncached("grok", 1)
    assert probe.status == health.TIMEOUT
    assert health._prescription("grok", "reinstall")[0] in probe.prescription
    assert probe.owner_pkg_manager == ""


def test_registry_covers_missing_and_unauthenticated():
    """The not-logged-in state has no equivalent in the Digg pattern and is
    the one users will actually hit after installing."""
    assert ("x", "grok_cli_missing") in prescriptions.REGISTRY
    assert ("x", "grok_not_authenticated") in prescriptions.REGISTRY


def test_not_authenticated_fix_is_a_login_not_an_install():
    entry = prescriptions.REGISTRY[("x", "grok_not_authenticated")]
    assert entry.fix_cli.startswith("grok login")
    assert "no X account" in entry.fix_nl


def test_new_entries_carry_no_secret_looking_values():
    for key in (("x", "grok_cli_missing"), ("x", "grok_not_authenticated")):
        entry = prescriptions.REGISTRY[key]
        blob = f"{entry.cause} {entry.fix_nl} {entry.fix_cli}"
        assert "AUTH_TOKEN=" not in blob and "API_KEY=" not in blob


def test_failed_grok_dependency_is_nl_only_in_doctor():
    from lib import doctor

    for state, kind in ((health.MISSING, "install"), (health.BROKEN, "reinstall"), (health.TIMEOUT, "reinstall")):
        text = health._prescription("grok", kind)[0]
        probe = health.DependencyProbe("grok", state, prescription=text)
        entry = prescriptions.for_dependency_probe(probe)
        assert entry.fix_cli == ""
        assert entry.fix_nl == text
        assert doctor._fix_text(entry) == text
    off_path = health.DependencyProbe("grok", health.MISSING, prescription="add /example/bin to PATH", off_path=True)
    assert prescriptions.for_dependency_probe(off_path).fix_cli == off_path.prescription
