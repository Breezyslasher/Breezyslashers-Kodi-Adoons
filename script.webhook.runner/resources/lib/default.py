import sys
import urllib.request
import urllib.parse
import xbmc
import xbmcaddon
import xbmcgui

addon = xbmcaddon.Addon()
MAX_ACTIONS = 10


def get_setting(id):
    return addon.getSetting(id)


def get_setting_bool(id):
    return addon.getSettingBool(id)


def show_notification(title, message, ms=2000):
    if get_setting_bool("show_notifications"):
        xbmc.executebuiltin(f'Notification({title},{message},{ms})')


def send_post(url, name="Webhook"):
    try:
        data = urllib.parse.urlencode({}).encode()
        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=10):
            show_notification("Webhook Sent", name)
            xbmc.log(f"[Webhook Runner] Sent: {name} -> {url}", xbmc.LOGINFO)
    except Exception as e:
        xbmc.log(f"[Webhook Runner] Error: {e}", xbmc.LOGERROR)
        show_notification("Webhook Error", str(e), 4000)


def run_action(i):
    url = get_setting(f"url_{i}")
    name = get_setting(f"name_{i}")
    enabled = get_setting_bool(f"enabled_{i}")

    if enabled and url:
        send_post(url, name)
    else:
        show_notification("Webhook Not Configured", f"Action {i} is disabled or missing URL")


def main():
    xbmc.log("[Webhook Runner] Started", xbmc.LOGINFO)

    params = sys.argv
    if len(params) > 1:
        for arg in params[1:]:
            if "id=" in arg:
                try:
                    action_id = int(arg.split("=")[1])
                    xbmc.log(f"[Webhook Runner] Running action {action_id}", xbmc.LOGINFO)
                    run_action(action_id)
                    return
                except Exception as e:
                    xbmc.log(f"[Webhook Runner] Invalid id parameter: {e}", xbmc.LOGERROR)
                    return

    # No ID -> show selection dialog
    actions = []
    for i in range(1, MAX_ACTIONS + 1):
        if get_setting_bool(f"enabled_{i}"):
            name = get_setting(f"name_{i}") or f"Action {i}"
            url = get_setting(f"url_{i}")
            if url:
                actions.append((i, name, url))

    if not actions:
        xbmcgui.Dialog().ok("Webhook Runner", "No enabled webhooks configured.")
        xbmc.log("[Webhook Runner] No actions enabled.", xbmc.LOGINFO)
        return

    names = [a[1] for a in actions]
    choice = xbmcgui.Dialog().select("Select Action", names)
    if choice >= 0:
        i, name, url = actions[choice]
        xbmc.log(f"[Webhook Runner] User selected {name}", xbmc.LOGINFO)
        send_post(url, name)


if __name__ == "__main__":
    main()
