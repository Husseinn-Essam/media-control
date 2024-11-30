
const VideoFeed = () => {
    return (
        <div>
            <h1>Live Video Feed</h1>
            <img 
                src="http://localhost:5000/video_feed" 
                alt="Video Stream" 
                style={{ width: '100%', height: 'auto' }}
            />
        </div>
    );
};

export default VideoFeed;
