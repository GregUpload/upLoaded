#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <stdio.h>
#include <wchar.h>
#include <stdlib.h>

#define IDR_PAYLOAD 101
#define APP_SUBDIR L"GregPythonBundle\\3.14.10"

static int make_dirs(const wchar_t *path) {
    wchar_t tmp[32768];
    size_t n = wcslen(path);
    if (n >= 32768) return 0;
    wcscpy(tmp, path);
    for (size_t i = 3; i < n; ++i) {
        if (tmp[i] == L'\\' || tmp[i] == L'/') {
            wchar_t c = tmp[i];
            tmp[i] = 0;
            if (wcslen(tmp) > 0) CreateDirectoryW(tmp, NULL);
            tmp[i] = c;
        }
    }
    if (CreateDirectoryW(tmp, NULL)) return 1;
    return GetLastError() == ERROR_ALREADY_EXISTS;
}

static int write_resource(const wchar_t *dest) {
    HRSRC r = FindResourceW(NULL, MAKEINTRESOURCEW(IDR_PAYLOAD), RT_RCDATA);
    if (!r) return 0;
    HGLOBAL loaded = LoadResource(NULL, r);
    if (!loaded) return 0;
    DWORD size = SizeofResource(NULL, r);
    const void *data = LockResource(loaded);
    if (!data || size == 0) return 0;

    HANDLE f = CreateFileW(dest, GENERIC_WRITE, 0, NULL, CREATE_ALWAYS,
                           FILE_ATTRIBUTE_NORMAL, NULL);
    if (f == INVALID_HANDLE_VALUE) return 0;
    const BYTE *p = (const BYTE *)data;
    DWORD remaining = size;
    int ok = 1;
    while (remaining) {
        DWORD chunk = remaining > 1024 * 1024 ? 1024 * 1024 : remaining;
        DWORD written = 0;
        if (!WriteFile(f, p, chunk, &written, NULL) || written != chunk) {
            ok = 0; break;
        }
        p += written;
        remaining -= written;
    }
    CloseHandle(f);
    return ok;
}

/* Quote a path for PowerShell's single-quoted string syntax. */
static int ps_quote(const wchar_t *src, wchar_t *dst, size_t cap) {
    size_t j = 0;
    if (cap < 3) return 0;
    dst[j++] = L'\'';
    for (size_t i = 0; src[i]; ++i) {
        if (src[i] == L'\'') {
            if (j + 2 >= cap) return 0;
            dst[j++] = L'\'';
            dst[j++] = L'\'';
        } else {
            if (j + 1 >= cap) return 0;
            dst[j++] = src[i];
        }
    }
    if (j + 2 > cap) return 0;
    dst[j++] = L'\'';
    dst[j] = 0;
    return 1;
}

static int run_powershell_extract(const wchar_t *zip, const wchar_t *dest) {
    wchar_t qzip[32768], qdest[32768], cmd[65535];
    if (!ps_quote(zip, qzip, 32768) || !ps_quote(dest, qdest, 32768))
        return 0;

    /* Expand-Archive is included with Windows PowerShell on supported Windows versions. */
    _snwprintf(cmd, 65534,
        L"powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass "
        L"-Command \"Expand-Archive -LiteralPath %s -DestinationPath %s -Force\"",
        qzip, qdest);
    cmd[65534] = 0;

    STARTUPINFOW si;
    PROCESS_INFORMATION pi;
    ZeroMemory(&si, sizeof(si));
    ZeroMemory(&pi, sizeof(pi));
    si.cb = sizeof(si);

    if (!CreateProcessW(NULL, cmd, NULL, NULL, FALSE,
                        CREATE_NO_WINDOW, NULL, NULL, &si, &pi))
        return 0;

    WaitForSingleObject(pi.hProcess, INFINITE);
    DWORD code = 1;
    GetExitCodeProcess(pi.hProcess, &code);
    CloseHandle(pi.hThread);
    CloseHandle(pi.hProcess);
    return code == 0;
}

static int run_python(const wchar_t *python, const wchar_t *script,
                      const wchar_t *working_dir) {
    wchar_t cmd[32768];
    _snwprintf(cmd, 32767, L"\"%s\" \"%s\"", python, script);
    cmd[32767] = 0;

    STARTUPINFOW si;
    PROCESS_INFORMATION pi;
    ZeroMemory(&si, sizeof(si));
    ZeroMemory(&pi, sizeof(pi));
    si.cb = sizeof(si);

    if (!CreateProcessW(python, cmd, NULL, NULL, FALSE, 0,
                        NULL, working_dir, &si, &pi)) {
        wchar_t msg[512];
        _snwprintf(msg, 511, L"Impossible de lancer Python (erreur Windows %lu).",
                   GetLastError());
        MessageBoxW(NULL, msg, L"Application", MB_ICONERROR | MB_OK);
        return 1;
    }

    WaitForSingleObject(pi.hProcess, INFINITE);
    DWORD code = 1;
    GetExitCodeProcess(pi.hProcess, &code);
    CloseHandle(pi.hThread);
    CloseHandle(pi.hProcess);
    return (int)code;
}

int WINAPI wWinMain(HINSTANCE instance, HINSTANCE prev, PWSTR cmdline, int show) {
    (void)instance; (void)prev; (void)cmdline; (void)show;

    wchar_t localapp[32768], root[32768], runtime[32768];
    wchar_t scripts[32768], python[32768], mainpy[32768];
    wchar_t payloadzip[32768], marker[32768];

    DWORD n = GetEnvironmentVariableW(L"LOCALAPPDATA", localapp, 32768);
    if (n == 0 || n >= 32768) {
        MessageBoxW(NULL, L"LOCALAPPDATA est introuvable.", L"Application",
                    MB_ICONERROR | MB_OK);
        return 1;
    }

    _snwprintf(root, 32767, L"%s\\%s", localapp, APP_SUBDIR);
    _snwprintf(runtime, 32767, L"%s\\runtime", root);
    _snwprintf(scripts, 32767, L"%s\\scripts", runtime);
    _snwprintf(python, 32767, L"%s\\python.exe", runtime);
    _snwprintf(mainpy, 32767, L"%s\\main.py", scripts);
    _snwprintf(payloadzip, 32767, L"%s\\payload.zip", root);
    _snwprintf(marker, 32767, L"%s\\install.ok", root);

    if (!make_dirs(root)) {
        MessageBoxW(NULL, L"Impossible de créer le dossier de travail.", L"Application",
                    MB_ICONERROR | MB_OK);
        return 1;
    }

    DWORD attr = GetFileAttributesW(marker);
    DWORD pyattr = GetFileAttributesW(python);
    if (attr == INVALID_FILE_ATTRIBUTES || pyattr == INVALID_FILE_ATTRIBUTES) {
        if (!write_resource(payloadzip)) {
            MessageBoxW(NULL, L"Impossible d'extraire la ressource embarquée.", L"Application",
                        MB_ICONERROR | MB_OK);
            return 1;
        }
        if (!run_powershell_extract(payloadzip, root)) {
            MessageBoxW(NULL,
                L"Décompression impossible. Vérifie que Windows PowerShell est disponible.",
                L"Application", MB_ICONERROR | MB_OK);
            return 1;
        }
        HANDLE mf = CreateFileW(marker, GENERIC_WRITE, 0, NULL, CREATE_ALWAYS,
                                FILE_ATTRIBUTE_NORMAL, NULL);
        if (mf != INVALID_HANDLE_VALUE) CloseHandle(mf);
        DeleteFileW(payloadzip);
    }

    /* Prevent user-site packages from changing the embedded environment. */
    SetEnvironmentVariableW(L"PYTHONNOUSERSITE", L"1");
    SetEnvironmentVariableW(L"PYTHONUTF8", L"1");

    return run_python(python, mainpy, scripts);
}
