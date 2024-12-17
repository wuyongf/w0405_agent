import json
import asyncio
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
from aiohttp import web
import cv2
import aiohttp_cors
from av import VideoFrame
from aiortc.rtcconfiguration import RTCConfiguration, RTCIceServer

class CameraStreamTrack(MediaStreamTrack):
    """
    A video track that captures frames from the robot's camera (using OpenCV)
    and sends them via WebRTC.
    """
    kind = "video"

    def __init__(self):
        super().__init__()
        self.cap = cv2.VideoCapture(2)  # Adjust this based on your camera index

        if not self.cap.isOpened():
            raise Exception("Could not open video device")

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    async def recv(self):
        loop = asyncio.get_event_loop()
        ret, frame = await loop.run_in_executor(None, self.cap.read)

        if not ret:
            raise Exception("Failed to capture image")

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        video_frame = VideoFrame.from_ndarray(frame_rgb, format="rgb24")
        video_frame.pts = self.cap.get(cv2.CAP_PROP_POS_MSEC)
        video_frame.time_base = 1 / 1000

        return video_frame

async def handle_offer(request):
    try:
        # Parse the incoming JSON body
        params = await request.json()
        offer_sdp = params['sdp']
        print(f"Received offer SDP:\n{offer_sdp}\n")

        # Create RTCIceServer objects for multiple STUN and TURN servers
        ice_servers = [
            RTCIceServer(urls="stun:stun.relay.metered.ca:80"),  # STUN server
            RTCIceServer(
                urls="turn:asia.relay.metered.ca:80",  # TURN server
                username="9ec1df6f1b773722904bad9c",   # TURN server username
                credential="+mveHp5VER8shj+X"          # TURN server password
            ),
            RTCIceServer(
                urls="turn:asia.relay.metered.ca:80?transport=tcp",  # TURN server over TCP
                username="9ec1df6f1b773722904bad9c",   # TURN server username
                credential="+mveHp5VER8shj+X"          # TURN server password
            ),
            RTCIceServer(
                urls="turn:asia.relay.metered.ca:443",  # TURN server over port 443
                username="9ec1df6f1b773722904bad9c",   # TURN server username
                credential="+mveHp5VER8shj+X"          # TURN server password
            ),
            RTCIceServer(
                urls="turns:asia.relay.metered.ca:443?transport=tcp",  # TURN server over TLS on port 443
                username="9ec1df6f1b773722904bad9c",   # TURN server username
                credential="+mveHp5VER8shj+X"          # TURN server password
            )
        ]

        # ice_servers = [
            
        #     RTCIceServer(urls="stun:stun2.l.google.com:19302"),  # Secondary STUN server
        #     RTCIceServer(urls="stun:stun.l.google.com:19302"),  # Third STUN server
        #     RTCIceServer(urls="stun:stun1.l.google.com:19302"),  # Primary STUN server
        #     RTCIceServer(
        #         urls="turn:relay1.expressturn.com:3478",  # Primary TURN server
        #         username="efINI7G0NQIXTCMYSA",           # TURN server username
        #         credential="spFQQ3qvZ7vkY0aY"            # TURN server password
        #     )
        # ]

        # Create WebRTC PeerConnection with RTCConfiguration containing iceServers
        configuration = RTCConfiguration(iceServers=ice_servers)
        peer_connection = RTCPeerConnection(configuration=configuration)

        # Logging for ICE candidate gathering
        @peer_connection.on("iceconnectionstatechange")
        async def on_iceconnectionstatechange():
            print(f"ICE connection state: {peer_connection.iceConnectionState}")

        @peer_connection.on("icegatheringstatechange")
        async def on_icegatheringstatechange():
            print(f"ICE gathering state: {peer_connection.iceGatheringState}")

        @peer_connection.on("icecandidate")
        async def on_icecandidate(candidate):
            if candidate:
                print(f"New ICE candidate found: {candidate}")
            else:
                print("All ICE candidates gathered.")

        # Add robot's camera stream to the peer connection
        video_track = CameraStreamTrack()
        peer_connection.addTrack(video_track)

        # Set the remote description (offer) from the WebUI
        offer = RTCSessionDescription(sdp=offer_sdp, type="offer")
        await peer_connection.setRemoteDescription(offer)

        # Create an answer
        answer = await peer_connection.createAnswer()
        await peer_connection.setLocalDescription(answer)

        # Print the answer to the terminal
        print(f"Generated answer SDP:\n{peer_connection.localDescription.sdp}\n")
        
        response = {
            'sdp': peer_connection.localDescription.sdp
        }
        return web.json_response(response)

    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        return web.json_response({'error': 'Invalid JSON input'}, status=400)

    except Exception as e:
        print(f"Error processing the offer: {e}")
        return web.json_response({'error': str(e)}, status=500)

# Initialize the web application and CORS support
app = web.Application()

# Setup CORS for cross-origin requests
cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
        allow_credentials=True,
        expose_headers="*",
        allow_headers="*",
        allow_methods=["POST", "OPTIONS"],
    )
})

# Define route for handling WebRTC offers
offer_route = app.router.add_post('/offer', handle_offer)
cors.add(offer_route)

if __name__ == '__main__':
    print("Robot WebRTC server started on port 8080.")
    web.run_app(app, port=8080)
