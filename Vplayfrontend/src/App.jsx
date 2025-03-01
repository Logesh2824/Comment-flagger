import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Login from './components/Login';
import Signup from './components/Signup';
import Home from './components/Home';
import UploadVideo from './components/UploadVideo';
import WatchVideo from './components/WatchVideo';
import SubscribedVideos from './components/SubscribedVideos';
import MyProfile from './components/MyProfile';
import WatchHistory from './components/watchHistory';// Import SubscribedVideos component
import Search from './components/Search';
import Front from './components/Frontp';
import Button from './components/Button';
function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Signup />} />
        <Route path="/login" element={<Login />} />
        <Route path="/home" element={<Home />} />
        <Route path="/upload" element={<UploadVideo />} />
        <Route path="/video/:filename" element={<WatchVideo />} />
        <Route path="/watch_history" element={<WatchHistory />} />
        <Route path="/my-profile" element={<MyProfile />} />
        <Route path="/front1" element={<Front />} />
        <Route path="/search" element={<Search />} />
        <Route path="/subscribed_videos" element={<SubscribedVideos />} /> {/* Add SubscribedVideos route */}
      </Routes>
    </Router>
  );
}

export default App;
