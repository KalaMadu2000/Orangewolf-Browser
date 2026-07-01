import os
import requests


class GetUpdate:
    def __init__(self, url):
        self.url = url

    def reach_for_update(self):
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            print(f"Error reaching for update: {e}")
            return None


class UpdateManager:
    def __init__(self, update_url):
        self.update_url = update_url

    def check_for_update(self):
        get_update = GetUpdate(self.update_url)
        return get_update.reach_for_update()


def get_version(text):
    for line in text.splitlines():
        if line.startswith("# UPDATE:"):
            return line.split(":", 1)[1].strip()
    return None


def version_tuple(version):
    return tuple(map(int, version.split(".")))


if __name__ == "__main__":

    update_urls = [
        "https://raw.githubusercontent.com/KalaMadu2000/Orangewolf-Browser/refs/heads/main/main.pyw",
        "https://raw.githubusercontent.com/KalaMadu2000/Orangewolf-Browser/refs/heads/main/update_manager.py"
    ]

    if not update_urls:
        print("No update URLs configured.")
        print("UPDATE-MANAGER > Epic fail from the creator :)")
        print("Adam Szigeti > SHUT UP")
        exit()

    with open("main.pyw", "r", encoding="utf-8") as f:
        current_text = f.read()

    current_version = get_version(current_text)

    if current_version is None:
        print("Current version not found.")
        exit()

    print(f"Current version: {current_version}")

    for url in update_urls:

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Failed to check update: {e}")
            continue

        remote_text = response.text
        latest_version = get_version(remote_text)

        if latest_version is None:
            print("Remote version not found.")
            continue

        print(f"Latest version: {latest_version}")

        if version_tuple(latest_version) > version_tuple(current_version):

            print(f"Update available: {latest_version}")

            update_manager = UpdateManager(url)
            result = update_manager.check_for_update()

            if result is None:
                print("Download failed.")
                continue

            update_folder = os.path.join("updates", latest_version)
            os.makedirs(update_folder, exist_ok=True)

            filename = os.path.basename(url)
            save_path = os.path.join(update_folder, filename)

            with open(save_path, "wb") as f:
                f.write(result)

            print(f"Update saved to: {save_path}")

        else:
            print("No update available.")