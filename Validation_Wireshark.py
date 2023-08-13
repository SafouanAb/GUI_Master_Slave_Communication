import requests

def download_wireshark():
    url = "https://2.na.dl.wireshark.org/win64/Wireshark-win64-4.0.7.exe"
    filename = "D:\\Wireshark-win64-4.0.7.exe"

    try:
        # Download Wireshark from the URL
        response = requests.get(url, stream=True)
        with open(filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        print(f"Wireshark downloaded successfully to {filename}")
    except Exception as e:
        print(f"Failed to download Wireshark. Error: {e}")

if __name__ == "__main__":
    download_wireshark()
