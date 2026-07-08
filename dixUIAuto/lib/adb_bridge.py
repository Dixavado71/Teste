"""
ADB Bridge - Abstração de comandos ADB
"""
import subprocess
import re
from typing import List, Optional, Tuple
from lib.logs import logger
from lib.exceptions import ADBError, DeviceNotFoundError


class ADBBridge:
    """Ponte para execução de comandos ADB."""
    
    def __init__(self, device_id: str = None):
        self.device_id = device_id
        self.log = logger.get_logger("ADB")
    
    def _run_command(self, command: str, timeout: int = 30) -> Tuple[bool, str]:
        """Executa comando shell e retorna (sucesso, output)."""
        try:
            self.log.debug(f"Executando: {command}")
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='utf-8',
                errors='ignore'
            )
            output = result.stdout + result.stderr
            success = result.returncode == 0
            return success, output.strip()
        except subprocess.TimeoutExpired:
            self.log.error(f"Timeout no comando: {command}")
            return False, "Timeout expired"
        except Exception as e:
            self.log.error(f"Erro ao executar comando: {e}")
            return False, str(e)
    
    def _adb_cmd(self, cmd: str, timeout: int = 30) -> Tuple[bool, str]:
        """Executa comando ADB com ou sem device_id."""
        if self.device_id:
            full_cmd = f"adb -s {self.device_id} {cmd}"
        else:
            full_cmd = f"adb {cmd}"
        return self._run_command(full_cmd, timeout)
    
    def get_devices(self) -> List[str]:
        """Lista dispositivos conectados."""
        success, output = self._run_command("adb devices")
        if not success:
            raise ADBError("devices", output)
        
        devices = []
        for line in output.split('\n')[1:]:
            if '\tdevice' in line:
                device_id = line.split('\t')[0]
                devices.append(device_id)
        
        self.log.info(f"Dispositivos encontrados: {len(devices)}")
        return devices
    
    def connect(self, host: str, port: int = 5555) -> bool:
        """Conecta a dispositivo via TCP/IP."""
        success, output = self._run_command(f"adb connect {host}:{port}")
        if success:
            self.log.success(f"Conectado a {host}:{port}")
        else:
            self.log.error(f"Falha ao conectar: {output}")
        return success
    
    def disconnect(self, host: str = None) -> bool:
        """Desconecta dispositivo(s)."""
        if host:
            cmd = f"adb disconnect {host}"
        else:
            cmd = "adb disconnect"
        success, output = self._run_command(cmd)
        return success
    
    def shell(self, command: str, timeout: int = 30) -> str:
        """Executa comando shell no dispositivo."""
        success, output = self._adb_cmd(f"shell \"{command}\"", timeout)
        if not success and output:
            raise ADBError(command, output)
        return output
    
    def start_app(self, package: str, activity: str = None) -> bool:
        """Inicia aplicativo."""
        if activity:
            cmd = f"am start -n {package}/{activity}"
        else:
            cmd = f"monkey -p {package} -c android.intent.category.LAUNCHER 1"
        success, output = self.shell(cmd)
        return success
    
    def stop_app(self, package: str) -> bool:
        """Para aplicativo."""
        cmd = f"am force-stop {package}"
        success, output = self.shell(cmd)
        return success
    
    def install(self, apk_path: str) -> bool:
        """Instala APK."""
        success, output = self._adb_cmd(f"install -r \"{apk_path}\"", timeout=120)
        if success:
            self.log.success(f"APK instalado: {apk_path}")
        else:
            self.log.error(f"Falha na instalação: {output}")
        return success
    
    def uninstall(self, package: str) -> bool:
        """Desinstala aplicativo."""
        cmd = f"uninstall {package}"
        success, output = self._adb_cmd(cmd)
        return success
    
    def pull(self, remote: str, local: str) -> bool:
        """Baixa arquivo do dispositivo."""
        cmd = f"pull \"{remote}\" \"{local}\""
        success, output = self._adb_cmd(cmd)
        return success
    
    def push(self, local: str, remote: str) -> bool:
        """Envia arquivo para o dispositivo."""
        cmd = f"push \"{local}\" \"{remote}\""
        success, output = self._adb_cmd(cmd)
        return success
    
    def screenshot(self, remote_path: str = "/sdcard/screenshot.png") -> bool:
        """Captura screenshot."""
        cmd = f"screencap -p {remote_path}"
        success, output = self.shell(cmd)
        return success
    
    def dump_ui(self, remote_path: str = "/sdcard/ui_dump.xml") -> bool:
        """Realiza dump da UI."""
        cmd = f"uiautomator dump {remote_path}"
        success, output = self.shell(cmd)
        return success
    
    def get_screen_size(self) -> Tuple[int, int]:
        """Obtém resolução da tela."""
        output = self.shell("wm size")
        match = re.search(r'(\d+)x(\d+)', output)
        if match:
            width, height = int(match.group(1)), int(match.group(2))
            return width, height
        return 1080, 1920  # Default
    
    def input_tap(self, x: int, y: int) -> bool:
        """Executa tap nas coordenadas."""
        cmd = f"input tap {x} {y}"
        success, output = self.shell(cmd)
        return success
    
    def input_swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300) -> bool:
        """Executa swipe."""
        cmd = f"input swipe {x1} {y1} {x2} {y2} {duration}"
        success, output = self.shell(cmd)
        return success
    
    def input_text(self, text: str) -> bool:
        """Digita texto."""
        # Escapar caracteres especiais
        escaped = text.replace(' ', '%s').replace('&', '\\&')
        cmd = f"input text \"{escaped}\""
        success, output = self.shell(cmd)
        return success
    
    def input_keyevent(self, keycode: int) -> bool:
        """Envia evento de tecla."""
        cmd = f"input keyevent {keycode}"
        success, output = self.shell(cmd)
        return success
    
    def is_screen_on(self) -> bool:
        """Verifica se tela está ligada."""
        output = self.shell("dumpsys power | grep mWakefulness")
        return "Asleep" not in output
    
    def wake_up(self) -> bool:
        """Liga a tela."""
        return self.input_keyevent(224)  # KEYCODE_WAKEUP
    
    def unlock(self) -> bool:
        """Tenta desbloquear dispositivo."""
        # Swipe simples para desbloquear
        w, h = self.get_screen_size()
        self.input_swipe(w // 2, h - 100, w // 2, h // 2)
        return True
    
    def get_current_package(self) -> str:
        """Obtém pacote em primeiro plano."""
        output = self.shell("dumpsys window windows | grep -E 'mCurrentFocus|mFocusedApp'")
        match = re.search(r'(\w+\.\w+)/', output)
        if match:
            return match.group(1)
        return ""
