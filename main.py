#@title Run APP
from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import json
import gradio as gr
import logging
import time
from google.colab import files

def web_driver(han):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    if not han:
        options.add_argument('--disable-gpu')
        options.add_argument('--remote-debugging-port=9222')
        options.add_argument('--enable-logging')
        options.add_argument('--log-level=0')
        options.set_capability("goog:loggingPrefs", {'performance': 'ALL'})
    driver = webdriver.Chrome(options=options)
    return driver

def download_video(url):
    driver = web_driver(han=True)
    try:
        driver.get(url)
        iframes = driver.find_elements(By.TAG_NAME, 'iframe')
        iframe_srcs = [iframe.get_attribute('src') for iframe in iframes]

        if len(iframe_srcs) == 0:
            driver.quit()
            return "No iframe found", None

        driver = web_driver(han=False)
        driver.get(iframe_srcs[0])
        logs = driver.get_log('performance')

        network_events = [json.loads(log['message'])['message'] for log in logs if 'Network' in log['message']]
        request_events = [event for event in network_events if event['method'] == 'Network.requestWillBeSent']
        
        filtered_urls = []
        for event in request_events:
            if 'request' in event['params']:
                url = event['params']['request']['url']
                if any(ext in url for ext in ['.vlxx']):
                    filtered_urls.append(url)

        if not filtered_urls:
            driver.quit()
            return "No downloadable video found", None

        video_url = str(filtered_urls[0].strip())
        output_file = "video.mp4"
        os.system(f"yt-dlp \"{video_url}\" -o {output_file}")

        driver.quit()
        
        download_status = "Video have been save in ./content/video.mp4"

        # files.download(output_file)

        return download_status
    except Exception as e:
        logging.error("Error occurred: %s", e)
        return str(e)
    finally:
        driver.quit()

# Create Gradio interface
interface = gr.Interface(
    fn=download_video, 
    # inputs=gr.Textbox(label="Video URL"),
    inputs=gr.Textbox(label="Video URL", placeholder="https://vlxx.mx/video/..."), 
    outputs=[gr.Text(label="Status")],
    title="Video Downloader",
    description="Enter the URL of the video page to download the video."
)

# Launch the app
interface.launch()
