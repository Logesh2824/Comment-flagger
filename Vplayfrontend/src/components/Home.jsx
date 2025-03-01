import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import VideoCard from './VideoCard';
import './home.css';
import logo from '../assets/logo-color.svg';

const Home = () => {
  const [videos, setVideos] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    fetchVideos();
  }, []);

  const fetchVideos = async () => {
    try {
      const response = await axios.get('http://localhost:5000/videos');
      setVideos(response.data);
    } catch (error) {
      console.error('Failed to fetch videos:', error);
    }
  };

  return (
    <div className="home">
      <header className="header">
        <div className="logo">
          <Link to="/">
            <img src={logo} alt="Website Logo" />
          </Link>
        </div>
        <nav className="nav">
        <Link to="/home" className="nav-link">Home</Link>
          <Link to="/upload" className="nav-link">Upload Video</Link>
          <Link to="/subscribed_videos" className="nav-link">Subscribed Videos</Link>
          <Link to="/watch_history" className="nav-link">WatchHistory</Link>
          <Link to="/search" className="nav-link">Search</Link>
        </nav>
        <div className="user-profile">
          <Link to="/my-profile">
            <img src="users.png" alt="User Profile" />
          </Link>
        </div>
      </header>
      <main className="main-content">
        <h1>Video Gallery</h1>
        <div className="videos-grid">
          {videos.map((video) => (
            <VideoCard key={video.file_id} video={video} />
          ))}
        </div>
      </main>
    </div>
  );
};

export default Home;
