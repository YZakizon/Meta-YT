class MetaYTError(Exception):
    """Base exception for inheritance."""

class VideoFetchError(MetaYTError):
    """
    Exception raised when failed to fetch api from YouTube

    This likely YouTube thinks you are robot, banned your IP
    or detect your IP is comming from datacenter
    """

    def __init__(self, videoId: str, status: str, message: str) -> None:
        self.status = status
        self.message = message
        self.videoId = videoId
        super().__init__(self.videoId, self.status, self.message)

    def __str__(self) -> str:
        return f"""VideoId: {self.videoId}, status: {self.status}, message: {self.message}
        - YouTube may think you are a robot 
        - YouTube has banned your IP address 
        - YouTube detects your IP address is coming from from a cloud datacenter IP address.
        """

class VideoUnavailable(MetaYTError):
    """
    Exception raised when a video is unavailable.

    :param videoId: The ID of the unavailable video.
    :type videoId: str
    """

    def __init__(self, videoId: str):
        """
        Initializes a `VideoUnavailable` exception instance.

        :param videoId: The ID of the unavailable video.
        :type videoId: str
        """
        self.videoId = videoId
        super().__init__(self._error_message)

    @property
    def _error_message(self) -> str:
        """
        Returns the error message for the VideoUnavailable exception.

        :return: The error message explaining why the video is unavailable.
        :rtype: str
        """
        return (
            f"Video ID: `{self.videoId}` is unavailable, it might be caused by various reasons such as:\n"
            "- Invalid Video ID\n"
            "- Video is private\n"
            "- Video is region locked"
        )
