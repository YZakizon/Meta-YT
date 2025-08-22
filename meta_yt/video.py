"""This module contains the developer interface for video fetching."""

import requests
import copy

from .caption import Caption
from .exceptions import VideoFetchError

YOUTUBE_API_KEY = "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8"


class Video:
    """
    A class to represent a YouTube video and fetch its details using the YouTube API.

    :param videoId: The ID of the YouTube video used to fetch its details.
    :type videoId: str
    :param retries: The number of retry attempts for fetching video details. Defaults to 5.
    :type retries: int
    """

    def __init__(self, videoId: str, retries: int = 5, proxies: list = []):
        """
        Initialize a Video object with details fetched from the YouTube API.

        :param videoId: The ID of the YouTube video used to fetch its details.
        :type videoId: str
        :param retries: The number of retry attempts for fetching video details. Defaults to 5.
        :type retries: int
        :param proxies: List of proxy dict. ie: [{'https': 'https://proxy1.com:8888', 'http': 'http://proxy2.com:8888'}, {'https': 'https://proxy3.com:8888'}]
        :type proxies: list 
        """
        url = "https://www.youtube.com/youtubei/v1/player"
        params = {
            "videoId": videoId,
            "key": YOUTUBE_API_KEY,
            "contentCheckOk": "True",
            "racyCheckOk": "True",
        }
        json_data = {
            "context": {
                "client": {
                    "clientName": "MWEB",
                    "clientVersion": "2.20211109.01.00",
                }
            },
            "api_key": YOUTUBE_API_KEY,
        }

        len_proxies = len(proxies)
        for attempt in range(retries):
            try:
                proxy = None
                if len_proxies > 0:
                    proxy = proxies[attempt % len_proxies]
                    # need to deep copy this, otherwise it altered the proxies variable
                    proxy = copy.deepcopy(proxy)
                    print(f"using proxies: {proxy}")

                response = requests.post(url, params=params, json=json_data, timeout=5, proxies=proxy)
                if response.status_code != 200:
                    print(f"get video details '{url}' failed status_code: {response.status_code}, json: {response.json()}")
                    
                response.raise_for_status()
                jsonResp = response.json()

                data = jsonResp.get("videoDetails", None)
                if not data:
                    playabilityStatus = jsonResp.get("playabilityStatus")
                    status = ""
                    reason = ""
                    if playabilityStatus:
                        status = playabilityStatus.get("status")
                        reason = playabilityStatus.get("reason")
                    raise VideoFetchError(videoId, status, reason)

                video_id = data["videoId"]
                channel_id = data["channelId"]
                thumbnails = data["thumbnail"]["thumbnails"]

                self.url = f"https://youtu.be/{video_id}"
                self.title = data["title"]
                self.video_id = video_id
                self.channel = data["author"]
                self.duration = int(data["lengthSeconds"])
                self.views = int(data["viewCount"])
                self.thumbnail = thumbnails[-1]["url"]
                self.thumbnails = thumbnails
                self.channel_id = channel_id
                self.channel_url = f"https://www.youtube.com/channel/{channel_id}"
                self.keywords = data.get("keywords", [])
                self.metadata = response.json()

                return
            except (requests.RequestException, KeyError) as e:
                if attempt < retries - 1:
                    pass
                else:
                    raise e

    def get_captions(self, include_generated: bool = False):
        """
        Retrieve caption tracks from metadata, filtering out auto-generated captions based on the `include_generated` parameter.

        :param include_generated: A boolean flag that determines whether auto-generated captions should be included in the result or not. If set to `True`, all captions, including auto-generated ones, will be returned. If set to `False`, auto-generated captions will be excluded. Defaults to False.
        :type include_generated: bool
        :return: A list of Caption objects.
        :rtype: list
        """
        captions = []
        for track in (
            self.metadata.get("captions", {})
            .get("playerCaptionsTracklistRenderer", {})
            .get("captionTracks", [])
        ):
            is_auto_generated = "auto-generated" in track.get("name", {}).get(
                "runs", [{}]
            )[0].get("text", "")

            if is_auto_generated and not include_generated:
                continue
            captions.append(
                Caption(track["baseUrl"], track["languageCode"], is_auto_generated)
            )

        return captions
